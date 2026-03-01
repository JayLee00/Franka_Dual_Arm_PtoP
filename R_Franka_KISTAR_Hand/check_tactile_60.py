#!/usr/bin/env python3
"""
Tactile 60개 검증 스크립트

1) SHM: Hand_j_tac[Hand_R][0..59] 60개 확인
2) ROS2: hand/state/right 의 tactile_sensors 60개 확인
3) HDF5: data/demo_*/Real_hand_tactile shape (N, 60) 확인

사용법:
  python3 check_tactile_60.py --shm
  python3 check_tactile_60.py --ros2
  python3 check_tactile_60.py --hdf5 [파일경로]
  python3 check_tactile_60.py --all [--hdf5 파일경로]
"""

import argparse
import ctypes
import struct
import sys
import time

# SHM 상수 (shm.h / monitor_shm.py와 동일)
SHM_KEY = 0x3940
Hand_Num = 2
Hand_DOF = 16
Kinesthetic_Sensor_DATA_NUM = 12
Tactile_Sensor_DATA_NUM = 60
Hand_R = 0


def align_offset(offset, alignment):
    if offset % alignment != 0:
        return offset + (alignment - (offset % alignment))
    return offset


def _shm_offset_hand_j_tac():
    offset = 0
    offset += 2
    offset += Hand_Num * Hand_DOF * 2
    offset += Hand_Num * Hand_DOF * 2
    offset += Hand_Num
    offset = align_offset(offset, 8)
    offset += Hand_Num * 8
    offset += Hand_Num * Hand_DOF * 2
    offset += Hand_Num * Kinesthetic_Sensor_DATA_NUM * 2
    return offset


def check_shm():
    """1) SHM에서 Hand_R Tactile 60개 읽기 및 검증"""
    print("\n" + "=" * 60)
    print("  [1] SHM Tactile 검증 (Hand_j_tac[Hand_R])")
    print("=" * 60)

    libc = ctypes.CDLL("libc.so.6")
    libc.shmget.argtypes = [ctypes.c_int, ctypes.c_size_t, ctypes.c_int]
    libc.shmget.restype = ctypes.c_int
    libc.shmat.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    libc.shmat.restype = ctypes.c_void_p
    libc.shmdt.argtypes = [ctypes.c_void_p]
    libc.shmdt.restype = ctypes.c_int

    shm_id = libc.shmget(SHM_KEY, 0, 0)
    if shm_id == -1:
        print("  ❌ SHM 없음 (R_Franka_KISTAR_Hand 또는 shm 생성 프로세스 먼저 실행)")
        return False

    ptr = libc.shmat(shm_id, None, 0)
    if ptr in (-1, None):
        print("  ❌ shmat 실패")
        return False

    base = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_uint8))
    off = _shm_offset_hand_j_tac()
    # Hand_R 쪽 60개 int16
    raw = bytes((base[off + i] for i in range(Tactile_Sensor_DATA_NUM * 2)))
    tac = list(struct.unpack(f"{Tactile_Sensor_DATA_NUM}h", raw))
    libc.shmdt(ptr)

    n = len(tac)
    ok = n == 60
    print(f"  개수: {n} (기대값: 60)  {'✅ OK' if ok else '❌ FAIL'}")
    print(f"  min/max/평균: {min(tac)} / {max(tac)} / {sum(tac)/len(tac):.1f}")
    print(f"  샘플 [0:5]: {tac[:5]}")
    print(f"  샘플 [55:60]: {tac[:60]}")
    return ok


def check_ros2():
    """2) ROS2 hand/state/right 구독하여 tactile_sensors 60개 검증"""
    print("\n" + "=" * 60)
    print("  [2] ROS2 토픽 Tactile 검증 (hand/state/right)")
    print("=" * 60)

    try:
        import rclpy
        from rclpy.node import Node
        from kistar_hand_ros2.msg import HandState
    except ImportError as e:
        print(f"  ❌ import 실패: {e}")
        print("     source install/setup.bash 후 실행하세요.")
        return False

    result = {"count": None, "ok": False, "done": False, "tac": None}

    class TactileSub(Node):
        def __init__(self):
            super().__init__("check_tactile_60_sub")
            self.sub = self.create_subscription(
                HandState, "hand/state/right", self.cb, 10
            )
            self.msg_count = 0

        def cb(self, msg):
            self.msg_count += 1
            if self.msg_count > 1:
                return
            tac = list(msg.tactile_sensors)
            n = len(tac)
            result["count"] = n
            result["ok"] = n == 60
            result["tac"] = tac
            result["done"] = True

    rclpy.init()
    node = TactileSub()
    timeout = 5.0
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout and not result["done"]:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()

    if result["count"] is None:
        print("  ❌ 5초 내 메시지 없음 (shm_ros2_bridge 실행 여부 확인)")
        return False

    n = result["count"]
    ok = result["ok"]
    tac = result.get("tac") or []
    print(f"  개수: {n} (기대값: 60)  {'✅ OK' if ok else '❌ FAIL'}")
    if tac:
        print(f"  min/max/평균: {min(tac)} / {max(tac)} / {sum(tac)/len(tac):.1f}")
        print(f"  샘플 [0:5]: {tac[:5]}, [55:60]: {tac[:60]}")
    if ok:
        print("  ROS2 토픽에서 tactile_sensors 60개 정상 수신")
    return ok


def check_hdf5(path: str):
    """3) HDF5 파일에서 Real_hand_tactile (N, 60) 검증"""
    print("\n" + "=" * 60)
    print("  [3] HDF5 로깅 Tactile 검증 (Real_hand_tactile)")
    print("=" * 60)
    print(f"  파일: {path}")

    try:
        import h5py
    except ImportError:
        print("  ❌ h5py 없음: pip install h5py")
        return False

    try:
        f = h5py.File(path, "r")
    except Exception as e:
        print(f"  ❌ 파일 열기 실패: {e}")
        return False

    if "data" not in f:
        print("  ❌ 'data' 그룹 없음")
        f.close()
        return False

    data = f["data"]
    demos = [k for k in data.keys() if k.startswith("demo_")]
    if not demos:
        print("  ❌ demo_* 그룹 없음")
        f.close()
        return False

    all_ok = True
    for name in sorted(demos)[:5]:
        grp = data[name]
        if "Real_hand_tactile" not in grp:
            print(f"  ❌ {name}: Real_hand_tactile 없음")
            all_ok = False
            continue
        dset = grp["Real_hand_tactile"]
        shape = dset.shape
        n_tac = shape[-1] if len(shape) >= 2 else shape[0]
        ok = n_tac == 60
        if not ok:
            all_ok = False
        print(f"  {name}: shape={shape}, 마지막 차원={n_tac}  {'✅' if ok else '❌'}")

    if len(demos) > 5:
        print(f"  ... 외 {len(demos) - 5}개 demo 생략")

    f.close()
    print(f"  결과: {'✅ 모두 60개' if all_ok else '❌ 일부 비정상'}")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Tactile 60개 검증 (SHM / ROS2 / HDF5)")
    parser.add_argument("--shm", action="store_true", help="SHM에서 Hand_R tactile 확인")
    parser.add_argument("--ros2", action="store_true", help="ROS2 hand/state/right tactile 확인")
    parser.add_argument("--hdf5", type=str, metavar="FILE", help="HDF5 파일에서 Real_hand_tactile 확인")
    parser.add_argument("--all", action="store_true", help="SHM + ROS2 (+ HDF5) 모두 실행")
    args = parser.parse_args()

    if not (args.shm or args.ros2 or args.hdf5 or args.all):
        parser.print_help()
        print("\n예: python3 check_tactile_60.py --all --hdf5 ./logs/hdf5_recordings/2026_02_28_15_46.hdf5")
        return 0

    results = []
    if args.all or args.shm:
        results.append(("SHM", check_shm()))
    if args.all or args.ros2:
        results.append(("ROS2", check_ros2()))
    if args.all or args.hdf5:
        path = args.hdf5 if args.hdf5 else None
        if path:
            results.append(("HDF5", check_hdf5(path)))
        elif args.all:
            print("\n  [3] HDF5: --hdf5 FILE 없음, 건너뜀")

    print("\n" + "=" * 60)
    print("  요약")
    print("=" * 60)
    for name, ok in results:
        print(f"  {name}: {'✅ OK' if ok else '❌ FAIL'}")
    print("=" * 60 + "\n")

    return 0 if all(r[1] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
