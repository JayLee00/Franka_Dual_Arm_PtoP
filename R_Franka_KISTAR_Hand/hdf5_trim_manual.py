#!/usr/bin/env python3
"""
HDF5 수동 트리밍 — 파일·데모·프레임 직접 지정

대화형 모드:
  python3 hdf5_trim_manual.py
  python3 hdf5_trim_manual.py --dir ./HDF5

CLI 원샷 모드:
  python3 hdf5_trim_manual.py input.hdf5 --demo 0   --front 50 --back 100
  python3 hdf5_trim_manual.py input.hdf5 --demo all  --front 30 --back 0
  python3 hdf5_trim_manual.py input.hdf5 --demo 0,2,3 --front 20 --back 50
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

import h5py
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# HDF5 유틸
# ─────────────────────────────────────────────────────────────────────────────

def list_hdf5_files(directory: str) -> list[str]:
    files = sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith('.hdf5') or f.endswith('.h5')
    )
    return files


def get_demo_info(h5file: h5py.File) -> list[dict]:
    """각 demo 의 기본 정보 반환."""
    if 'data' not in h5file:
        return []
    infos = []
    for dk in sorted(h5file['data'].keys()):
        grp = h5file['data'][dk]
        N   = len(grp['Real_timestamps'][:])
        ts  = grp['Real_timestamps'][:]
        ba  = grp['Real_bulb_angle'][:]
        dur = ts[-1] - ts[0] if N > 1 else 0.0
        hz  = (N - 1) / dur if dur > 0 else 0.0
        infos.append({
            'key':     dk,
            'frames':  N,
            'dur_sec': dur,
            'hz':      hz,
            'ba_min':  float(ba.min()),
            'ba_max':  float(ba.max()),
        })
    return infos


def print_demo_table(infos: list[dict]) -> None:
    print(f"\n  {'#':<4} {'demo key':<12} {'프레임':>7} {'시간(s)':>8} {'Hz':>6}  bulb range (deg)")
    print("  " + "-" * 62)
    for i, d in enumerate(infos):
        print(f"  {i:<4} {d['key']:<12} {d['frames']:>7} {d['dur_sec']:>8.2f} {d['hz']:>6.1f}"
              f"  {d['ba_min']:+.1f} ~ {d['ba_max']:+.1f}")


def trim_and_save(
    src_path:  str,
    dst_path:  str,
    cuts:      dict[str, tuple[int, int]],  # demo_key -> (front_cut, back_cut)
) -> None:
    """
    cuts: { 'demo_0': (front_frames, back_frames), ... }
    back_cut=0 이면 끝까지 유지.
    """
    with h5py.File(src_path, 'r') as src, h5py.File(dst_path, 'w') as dst:
        # root / data attrs 복사
        for k, v in src.attrs.items():
            dst.attrs[k] = v
        dst_data = dst.create_group('data')
        for k, v in src['data'].attrs.items():
            dst_data.attrs[k] = v

        total = 0
        for dk in sorted(src['data'].keys()):
            src_grp = src['data'][dk]
            dst_grp = dst_data.create_group(dk)

            front, back = cuts.get(dk, (0, 0))
            N = len(src_grp['Real_timestamps'][:])

            s = front
            e = N - back if back > 0 else N
            e = max(s + 1, e)   # 최소 1 프레임 보장

            for key in src_grp.keys():
                arr         = src_grp[key][:]
                arr_trimmed = arr[s:e]
                if key == 'Real_timestamps':
                    arr_trimmed = arr_trimmed - arr_trimmed[0]
                dst_grp.create_dataset(
                    key, data=arr_trimmed, compression='gzip', compression_opts=4)

            for ak, av in src_grp.attrs.items():
                dst_grp.attrs[ak] = av
            kept = e - s
            dst_grp.attrs['num_samples']    = kept
            dst_grp.attrs['trim_front']     = front
            dst_grp.attrs['trim_back']      = back
            total += kept

        dst_data.attrs['total'] = total


# ─────────────────────────────────────────────────────────────────────────────
# 입력 헬퍼
# ─────────────────────────────────────────────────────────────────────────────

def ask(prompt: str, default: str = '') -> str:
    val = input(prompt).strip()
    return val if val else default


def ask_int(prompt: str, default: int = 0, min_val: int = 0) -> int:
    while True:
        raw = ask(f"{prompt} (기본 {default}): ", str(default))
        try:
            v = int(raw)
            if v < min_val:
                print(f"  {min_val} 이상 입력하세요.")
                continue
            return v
        except ValueError:
            print("  정수를 입력하세요.")


def choose_file(directory: str) -> str | None:
    files = list_hdf5_files(directory)
    if not files:
        print(f"[ERROR] {directory} 에 .hdf5 파일이 없습니다.")
        return None

    print(f"\n── HDF5 파일 목록 ({directory}) ──")
    for i, f in enumerate(files):
        size_mb = os.path.getsize(f) / 1024 / 1024
        print(f"  {i}  {os.path.basename(f)}  ({size_mb:.1f} MB)")

    while True:
        raw = ask(f"\n파일 번호 또는 경로 입력: ").strip()
        if os.path.isfile(raw):
            return raw
        try:
            idx = int(raw)
            if 0 <= idx < len(files):
                return files[idx]
        except ValueError:
            pass
        print("  다시 입력하세요.")


def choose_demos(infos: list[dict]) -> list[str]:
    """선택할 demo key 목록 반환."""
    print_demo_table(infos)
    print("\n  입력 예) 0        → demo_0 만")
    print("          0,1,3    → 여러 개")
    print("          all      → 전체 (기본)")
    raw = ask("\n데모 번호 선택 (기본 all): ", "all").lower()

    if raw == 'all':
        return [d['key'] for d in infos]

    keys = []
    for tok in raw.split(','):
        tok = tok.strip()
        try:
            idx = int(tok)
            if 0 <= idx < len(infos):
                keys.append(infos[idx]['key'])
            else:
                print(f"  [WARN] 인덱스 {idx} 범위 초과 — 건너뜀")
        except ValueError:
            print(f"  [WARN] '{tok}' 파싱 불가 — 건너뜀")

    return keys if keys else [d['key'] for d in infos]


def preview_cuts(infos: list[dict], selected_keys: list[str],
                 front: int, back: int) -> None:
    print("\n── 트리밍 미리보기 ──")
    key_to_info = {d['key']: d for d in infos}
    for dk in selected_keys:
        d = key_to_info[dk]
        N = d['frames']
        s = front
        e = N - back if back > 0 else N
        kept = max(0, e - s)
        print(f"  {dk}: {N:5d}프레임  →  [{s} ~ {e})  유지={kept}프레임"
              f"  ({kept / d['hz']:.2f}s)  "
              f"앞-{s} / 뒤-{N - e}")
    non_selected = [d['key'] for d in infos if d['key'] not in selected_keys]
    if non_selected:
        print(f"  (미선택 demo 는 그대로 복사: {non_selected})")


# ─────────────────────────────────────────────────────────────────────────────
# 대화형 모드
# ─────────────────────────────────────────────────────────────────────────────

def interactive_mode(start_dir: str) -> None:
    # 1. 파일 선택
    src_path = choose_file(start_dir)
    if src_path is None:
        return

    print(f"\n선택한 파일: {src_path}")

    with h5py.File(src_path, 'r') as f:
        infos = get_demo_info(f)

    if not infos:
        print("[ERROR] 'data' 그룹 또는 demo 없음.")
        return

    # 2. 데모 선택
    selected_keys = choose_demos(infos)
    print(f"\n선택 demo: {selected_keys}")

    # 3. 프레임 입력
    key_to_info = {d['key']: d for d in infos}
    min_frames  = min(key_to_info[k]['frames'] for k in selected_keys)
    print(f"\n선택 demo 최소 프레임: {min_frames}")

    front = ask_int("앞에서 자를 프레임 수", default=0, min_val=0)
    back  = ask_int("뒤에서 자를 프레임 수 (0=끝까지 유지)", default=0, min_val=0)

    # 4. 미리보기
    preview_cuts(infos, selected_keys, front, back)

    # 5. 출력 경로
    base, ext = os.path.splitext(src_path)
    default_out = base + f'_cut_f{front}_b{back}' + ext
    out_path = ask(f"\n출력 파일 경로 (기본: {default_out}): ", default_out)

    # 같은 경로면 백업
    if os.path.abspath(out_path) == os.path.abspath(src_path):
        bak = src_path + '.bak'
        shutil.copy2(src_path, bak)
        print(f"  원본 백업: {bak}")

    # 6. 확인
    confirm = ask("\n저장하시겠습니까? (y/n, 기본 y): ", "y").lower()
    if confirm != 'y':
        print("  취소됨.")
        return

    # 7. 저장
    # 선택 demo: front/back 적용. 미선택 demo: (0, 0) = 전체 유지
    cuts: dict[str, tuple[int, int]] = {}
    for d in infos:
        if d['key'] in selected_keys:
            cuts[d['key']] = (front, back)
        else:
            cuts[d['key']] = (0, 0)

    trim_and_save(src_path, out_path, cuts)
    print(f"\n저장 완료: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI 원샷 모드
# ─────────────────────────────────────────────────────────────────────────────

def cli_mode(args) -> None:
    src_path = args.input
    if not os.path.isfile(src_path):
        print(f"[ERROR] 파일 없음: {src_path}")
        sys.exit(1)

    with h5py.File(src_path, 'r') as f:
        infos = get_demo_info(f)

    if not infos:
        print("[ERROR] demo 없음.")
        sys.exit(1)

    # demo 선택
    if args.demo.lower() == 'all':
        selected_keys = [d['key'] for d in infos]
    else:
        idx_list = [int(x.strip()) for x in args.demo.split(',')]
        selected_keys = []
        for idx in idx_list:
            if 0 <= idx < len(infos):
                selected_keys.append(infos[idx]['key'])
            else:
                print(f"[WARN] demo 인덱스 {idx} 범위 초과")

    if not selected_keys:
        print("[ERROR] 선택된 demo 없음.")
        sys.exit(1)

    front = args.front
    back  = args.back

    print(f"파일   : {src_path}")
    print(f"demo   : {selected_keys}")
    print(f"front  : {front}  back: {back}")
    preview_cuts(infos, selected_keys, front, back)

    # 출력 경로
    if args.output:
        out_path = args.output
    else:
        base, ext = os.path.splitext(src_path)
        out_path  = base + f'_cut_f{front}_b{back}' + ext

    if os.path.abspath(out_path) == os.path.abspath(src_path):
        bak = src_path + '.bak'
        shutil.copy2(src_path, bak)
        print(f"원본 백업: {bak}")

    cuts: dict[str, tuple[int, int]] = {}
    for d in infos:
        cuts[d['key']] = (front, back) if d['key'] in selected_keys else (0, 0)

    trim_and_save(src_path, out_path, cuts)
    print(f"저장 완료: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description='HDF5 수동 트리밍 (파일·데모·프레임 직접 지정)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('input',   nargs='?', default=None,
                        help='입력 HDF5 파일 (생략 시 대화형 모드)')
    parser.add_argument('--dir',   default='./HDF5',
                        help='대화형 모드에서 탐색할 폴더')
    parser.add_argument('--demo',  default='all',
                        help='자를 demo 번호: 0 / 0,1,3 / all')
    parser.add_argument('--front', type=int, default=0,
                        help='앞에서 자를 프레임 수')
    parser.add_argument('--back',  type=int, default=0,
                        help='뒤에서 자를 프레임 수 (0=끝까지 유지)')
    parser.add_argument('--output', '-o', default=None,
                        help='출력 파일 경로 (생략 시 자동)')
    args = parser.parse_args()

    if args.input is None:
        # 대화형 모드
        search_dir = args.dir if os.path.isdir(args.dir) else '.'
        interactive_mode(search_dir)
    else:
        cli_mode(args)


if __name__ == '__main__':
    main()
