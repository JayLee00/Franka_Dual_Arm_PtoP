#!/usr/bin/env python3
"""
HDF5 트리밍: 전구 회전 시작 ~ 종료 구간만 남기기

HDF5 파일 내 각 demo의 Real_bulb_angle 을 기반으로
  - 시작: 전구 각도가 angle_thresh(deg)를 넘어간 첫 프레임
  - 종료: 같은 각도로 still_duration(초) 동안 유지 → 해당 시점에서 자름

시작 감지: |bulb_angle| > angle_thresh (deg) 인 첫 프레임 (기본 10도)
종료 감지: 앞에서부터 스캔하면서 이후 still_duration(초) 동안
           각도 변화량 < still_thresh(deg) 인 첫 프레임 (기본 2초, 0.1deg)

사용 예:
  python3 hdf5_trim_bulb_start_end.py input.hdf5
  python3 hdf5_trim_bulb_start_end.py ./HDF5/                # 폴더 일괄 처리
  python3 hdf5_trim_bulb_start_end.py input.hdf5 --dry_run   # 미리 보기
  python3 hdf5_trim_bulb_start_end.py input.hdf5 \\
      --angle_thresh  10.0 \\  # 시작: 각도 초과 임계값 (deg, 기본 10)
      --still_duration 2.0  \\  # 종료: 같은 각도 유지 시간 (초, 기본 2)
      --still_thresh  0.1       # 종료: "같은 각도" 허용 오차 (deg, 기본 0.1)
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings

import h5py
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# 시작 인덱스 감지
# ─────────────────────────────────────────────────────────────────────────────

def find_bulb_start(
    bulb_angle: np.ndarray,
    timestamps: np.ndarray,
    angle_thresh: float = 20.0,
    lookback:     int   = 0,
) -> int:
    """
    전구 각도가 angle_thresh(deg)를 넘어간 첫 프레임 인덱스를 반환.

    Args:
        bulb_angle   : (N,) 로봇 전구 누적 회전각 (deg)
        timestamps   : (N,) 타임스탬프 (초)
        angle_thresh : 시작 감지 각도 임계값 (deg), 기본 10
        lookback     : 감지 인덱스에서 몇 프레임 앞으로 되돌릴지 (기본 0)

    Returns:
        start_idx: 잘라낼 시작 인덱스 (0 이상)
    """
    hits = np.where(np.abs(bulb_angle) > angle_thresh)[0]
    if len(hits) > 0:
        return max(0, int(hits[0]) - lookback)
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# 종료 인덱스 감지
# ─────────────────────────────────────────────────────────────────────────────

def find_bulb_end(
    bulb_angle:      np.ndarray,
    timestamps:      np.ndarray,
    still_duration:  float = 2.0,
    still_thresh:    float = 0.1,
) -> int:
    """
    전구 각도가 still_duration 초 동안 still_thresh deg 미만으로 변화(같은 각도 유지)하는
    첫 프레임 인덱스를 반환 → 그 지점에서 데이터를 자름.

    Args:
        bulb_angle      : (N,) 로봇 전구 누적 회전각 (deg)
        timestamps      : (N,) 타임스탬프 (초)
        still_duration  : 정지 판정 지속 시간 (초)
        still_thresh    : 정지 판정 각도 변화 임계값 (deg)

    Returns:
        end_idx: 잘라낼 끝 인덱스 (exclusive). N 이면 끝까지 유지.
    """
    N = len(bulb_angle)
    if N < 2:
        return N

    for i in range(N):
        t_window_end = timestamps[i] + still_duration

        # 윈도우 끝이 데이터 범위를 벗어나면 → still 확인 불가 → 전부 유지
        if t_window_end > timestamps[-1]:
            break

        j = int(np.searchsorted(timestamps, t_window_end, side='right'))
        window = bulb_angle[i:j]

        if np.max(np.abs(window - window[0])) < still_thresh:
            return i   # 이 프레임부터 still_duration 동안 안 움직임 → 여기서 자름

    return N   # still 구간 없음 → 끝까지 유지


# ─────────────────────────────────────────────────────────────────────────────
# demo 단위 트리밍
# ─────────────────────────────────────────────────────────────────────────────

def trim_demo(
    src_grp:        h5py.Group,
    dst_grp:        h5py.Group,
    angle_thresh:   float,
    lookback:       int,
    still_duration: float,
    still_thresh:   float,
) -> dict:
    """
    src_grp 에서 데이터를 읽어 트리밍 후 dst_grp 에 씀.

    Returns:
        info dict (start_idx, original_len, trimmed_len)
    """
    bulb_angle = src_grp['Real_bulb_angle'][:]
    timestamps = src_grp['Real_timestamps'][:]
    N_orig = len(timestamps)

    start_idx = find_bulb_start(
        bulb_angle, timestamps,
        angle_thresh=angle_thresh,
        lookback=lookback,
    )

    # 시작 이후 구간에서 종료 인덱스 감지 (start_idx 기준 상대 인덱스)
    end_idx_rel = find_bulb_end(
        bulb_angle[start_idx:],
        timestamps[start_idx:] - timestamps[start_idx],
        still_duration=still_duration,
        still_thresh=still_thresh,
    )
    end_idx = start_idx + end_idx_rel   # 원본 배열 절대 인덱스

    # 빈 구간 방지: end_idx <= start_idx 이면 최소 1프레임 유지
    if end_idx <= start_idx:
        end_idx = min(start_idx + 1, N_orig)
        warnings.warn(
            f"trim_demo: 빈 구간 감지 (start={start_idx}, end_rel={end_idx_rel}) → end_idx={end_idx}로 조정. "
            "전구가 시작 직후 정지했거나 still_duration/still_thresh를 확인하세요.",
            UserWarning,
            stacklevel=2,
        )

    # 모든 키 트리밍해서 dst 에 저장
    for key in src_grp.keys():
        arr = src_grp[key][:]
        arr_trimmed = arr[start_idx:end_idx]

        # timestamps 는 0 기준으로 재설정 (빈 배열이면 스킵)
        if key == 'Real_timestamps' and len(arr_trimmed) > 0:
            arr_trimmed = arr_trimmed - arr_trimmed[0]

        dst_grp.create_dataset(key, data=arr_trimmed, compression='gzip', compression_opts=4)

    # attrs 복사
    for attr_k, attr_v in src_grp.attrs.items():
        dst_grp.attrs[attr_k] = attr_v
    trimmed_len = end_idx - start_idx
    dst_grp.attrs['num_samples']      = trimmed_len
    dst_grp.attrs['trim_start_idx']   = start_idx
    dst_grp.attrs['trim_end_idx']     = end_idx

    return {
        'start_idx':    start_idx,
        'end_idx':      end_idx,
        'original_len': N_orig,
        'trimmed_len':  trimmed_len,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 파일 단위 처리
# ─────────────────────────────────────────────────────────────────────────────

def process_file(
    src_path:       str,
    dst_path:       str,
    angle_thresh:   float,
    lookback:       int,
    still_duration: float,
    still_thresh:   float,
    dry_run:        bool = False,
) -> None:
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}파일 처리: {src_path}")
    print(f"  → 출력: {dst_path}")

    with h5py.File(src_path, 'r') as src:
        if 'data' not in src:
            print("  [WARN] 'data' 그룹 없음 — 건너뜀")
            return

        demo_keys = sorted(src['data'].keys())
        print(f"  demo 수: {len(demo_keys)}")

        if dry_run:
            # 트리밍 결과만 미리 보기 (파일 저장 없음)
            for dk in demo_keys:
                grp  = src['data'][dk]
                ba   = grp['Real_bulb_angle'][:]
                ts   = grp['Real_timestamps'][:]
                N    = len(ts)

                sidx = find_bulb_start(ba, ts, angle_thresh=angle_thresh, lookback=lookback)
                eidx_rel = find_bulb_end(
                    ba[sidx:], ts[sidx:] - ts[sidx],
                    still_duration=still_duration, still_thresh=still_thresh,
                )
                eidx = sidx + eidx_rel

                kept  = eidx - sidx
                front = sidx
                back  = N - eidx
                ba_s  = ba[sidx]
                ba_e  = ba[eidx - 1] if eidx > sidx else float('nan')
                ts_s  = ts[sidx]
                ts_e  = ts[eidx - 1] if eidx > sidx else float('nan')
                print(f"  {dk}: [{sidx:5d} ~ {eidx:5d}) / {N:5d}  "
                      f"유지={kept}프레임  앞-{front} 뒤-{back}  "
                      f"bulb {ba_s:+.1f}→{ba_e:+.1f}deg  "
                      f"t={ts_s:.2f}~{ts_e:.2f}s")
            return

        # 실제 저장
        with h5py.File(dst_path, 'w') as dst:
            dst_data = dst.create_group('data')

            # root attrs 복사
            for k, v in src.attrs.items():
                dst.attrs[k] = v
            for k, v in src['data'].attrs.items():
                dst_data.attrs[k] = v

            total_orig    = 0
            total_trimmed = 0

            for dk in demo_keys:
                src_grp = src['data'][dk]
                dst_grp = dst_data.create_group(dk)

                info = trim_demo(
                    src_grp, dst_grp,
                    angle_thresh, lookback,
                    still_duration, still_thresh,
                )
                total_orig    += info['original_len']
                total_trimmed += info['trimmed_len']

                ba   = src_grp['Real_bulb_angle'][:]
                ts   = src_grp['Real_timestamps'][:]
                sidx = info['start_idx']
                eidx = info['end_idx']
                ba_s = ba[sidx]
                ba_e = ba[eidx - 1] if eidx > sidx else float('nan')
                ts_s = ts[sidx]
                ts_e = ts[eidx - 1] if eidx > sidx else float('nan')
                front = sidx
                back  = info['original_len'] - eidx
                print(f"  {dk}: {info['original_len']:5d} → {info['trimmed_len']:5d}프레임  "
                      f"(앞-{front} 뒤-{back} 제거)  "
                      f"bulb {ba_s:+.1f}→{ba_e:+.1f}deg  "
                      f"t={ts_s:.2f}~{ts_e:.2f}s")

            dst_data.attrs['total'] = total_trimmed
            trim_total_pct = (total_orig - total_trimmed) / max(total_orig, 1) * 100
            print(f"\n  총계: {total_orig:,} → {total_trimmed:,} 프레임  "
                  f"({trim_total_pct:.1f}% 제거)")
            print(f"  저장 완료: {dst_path}")


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def default_output_path(src_path: str) -> str:
    base, ext = os.path.splitext(src_path)
    return base + '_trimmed' + ext


def main() -> None:
    parser = argparse.ArgumentParser(
        description='HDF5 전구 돌리기 시작 시점 트리밍',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('input',
                        help='입력 HDF5 파일 또는 폴더 경로')
    parser.add_argument('--output', '-o', default=None,
                        help='출력 경로 (파일 or 폴더). 생략 시 input에 _trimmed 접미사')
    parser.add_argument('--angle_thresh',   type=float, default=10.0,
                        help='시작: 전구 각도 초과 임계값 (deg, 기본 10)')
    parser.add_argument('--lookback',       type=int,   default=0,
                        help='시작 시점 앞 유지 프레임 (기본 0)')
    parser.add_argument('--still_duration', type=float, default=2.0,
                        help='종료: 같은 각도 유지 시간 (초, 기본 2)')
    parser.add_argument('--still_thresh',   type=float, default=0.1,
                        help='종료: "같은 각도" 허용 오차 (deg, 기본 0.1)')
    parser.add_argument('--dry_run', action='store_true',
                        help='실제 저장 없이 트리밍 결과만 미리 보기')
    args = parser.parse_args()

    inp = args.input

    # ── 폴더 모드 ─────────────────────────────────────────────────────────────
    if os.path.isdir(inp):
        files = sorted(
            os.path.join(inp, f) for f in os.listdir(inp)
            if (f.endswith('.hdf5') or f.endswith('.h5')) and '_trimmed' not in f
        )
        if not files:
            print(f"[ERROR] 폴더에 .hdf5 파일 없음: {inp}")
            sys.exit(1)

        out_dir = args.output if args.output else inp
        os.makedirs(out_dir, exist_ok=True)

        for src_path in files:
            fname   = os.path.basename(src_path)
            base, ext = os.path.splitext(fname)
            dst_path = os.path.join(out_dir, base + '_trimmed' + ext)
            try:
                process_file(src_path, dst_path,
                             args.angle_thresh, args.lookback,
                             args.still_duration, args.still_thresh,
                             dry_run=args.dry_run)
            except OSError as e:
                print(f"  [SKIP] 파일 열기 실패 (손상/잘림 가능): {e}")

    # ── 단일 파일 모드 ────────────────────────────────────────────────────────
    elif os.path.isfile(inp):
        dst_path = args.output if args.output else default_output_path(inp)
        try:
            process_file(inp, dst_path,
                         args.angle_thresh, args.lookback,
                         args.still_duration, args.still_thresh,
                         dry_run=args.dry_run)
        except OSError as e:
            print(f"[ERROR] 파일 열기 실패 (손상/잘림 가능): {e}")
            sys.exit(1)
    else:
        print(f"[ERROR] 경로 없음: {inp}")
        sys.exit(1)


if __name__ == '__main__':
    main()
