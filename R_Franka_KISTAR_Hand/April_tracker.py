from __future__ import annotations

import math
import time
import ctypes
import ctypes.util
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
import pyrealsense2 as rs
from pupil_apriltags import Detector


# =========================
# CONFIG 
# =========================

TAG_FAMILY = "tag36h11"
TAG_SIZE_M = 0.0215  # [m] 실제 태그 한 변 길이
CUBE_SIZE_M = 0.055  # [m] 큐브 한 변 길이(대략), center_offset 계산에 사용

# 2x2 tags per face
ROWS = 2
COLS = 2
FACE_COUNT = 6
BASE_TAG_ID = 200

# tag grid spacing:
# - 태그가 딱 붙어있으면: TAG_SIZE_M
# - 태그 사이 간격(gap)이 있으면: TAG_SIZE_M + gap
TAG_GAP_M = 0.005
TAG_SPACING_M = TAG_SIZE_M + TAG_GAP_M

# cube center offset:
# 태그 좌표계에서 "태그 중심 -> 큐브 중심" 벡터의 z 성분 크기.
# 단, tag 좌표계 z 방향 정의/라이브러리에 따라 부호가 달라질 수 있어.
# 보통은 큐브 중심이 태그 뒤쪽이면 -CUBE_SIZE_M/2 쪽이 될 수 있음.
CENTER_OFFSET_M = 0.030

# face별 orientation (tag frame -> cube frame)용 기본 RPY(deg)
# face index 0..5 배치: 0=top, 1=back, 2=left, 3=right, 4=front, 5=bottom
FACE_ORDER: Tuple[str, ...] = ("top", "back", "left", "right", "front", "bottom")
DEFAULT_FACE_RPY_DEG_BY_FACE = {
    "top": (0.0, 0.0, 0.0),
    "back": (-90.0, 0.0, 0.0),
    "left": (0.0, 90.0, 0.0),
    "right": (0.0, -90.0, 90.0),
    "front": (90.0, 0.0, 0.0),
    "bottom": (0.0, 180.0, 90.0),
}
DEFAULT_FACE_RPY_DEG: Tuple[Tuple[float, float, float], ...] = tuple(
    DEFAULT_FACE_RPY_DEG_BY_FACE[name] for name in FACE_ORDER
)

# cube pose 계산 방식:
# - "nearest": 가장 가까운 태그 1개로 cube pose 결정 (가장 단순/안정적)
# - "fuse": 보이는 태그들로 translation/rotation 평균 (조금 더 부드러움)
POSE_MODE = "fuse"  # "nearest" or "fuse"

# simple temporal smoothing (0=no smoothing, 1=use only current)
SMOOTH_TRANSLATION_ALPHA = 0.7
SMOOTH_ROTATION_ALPHA = 0.7


# =========================
# math utils
# =========================

def euler_xyz_to_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    rx = np.array([[1, 0, 0],
                   [0, cr, -sr],
                   [0, sr, cr]], dtype=float)
    ry = np.array([[cp, 0, sp],
                   [0, 1, 0],
                   [-sp, 0, cp]], dtype=float)
    rz = np.array([[cy, -sy, 0],
                   [sy, cy, 0],
                   [0, 0, 1]], dtype=float)
    return rx @ ry @ rz


def rotation_translation_to_matrix(R: np.ndarray, t: np.ndarray) -> np.ndarray:
    T = np.eye(4, dtype=float)
    T[:3, :3] = R
    T[:3, 3] = t.reshape(3)
    return T


def matrix_to_rt(T: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    return T[:3, :3].copy(), T[:3, 3].copy()


def rotation_matrix_to_quaternion(R: np.ndarray) -> Tuple[float, float, float, float]:
    tr = float(np.trace(R))
    if tr > 0.0:
        s = math.sqrt(tr + 1.0) * 2.0
        qw = 0.25 * s
        qx = (R[2, 1] - R[1, 2]) / s
        qy = (R[0, 2] - R[2, 0]) / s
        qz = (R[1, 0] - R[0, 1]) / s
    else:
        if R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
            s = math.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2.0
            qw = (R[2, 1] - R[1, 2]) / s
            qx = 0.25 * s
            qy = (R[0, 1] + R[1, 0]) / s
            qz = (R[0, 2] + R[2, 0]) / s
        elif R[1, 1] > R[2, 2]:
            s = math.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2.0
            qw = (R[0, 2] - R[2, 0]) / s
            qx = (R[0, 1] + R[1, 0]) / s
            qy = 0.25 * s
            qz = (R[1, 2] + R[2, 1]) / s
        else:
            s = math.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2.0
            qw = (R[1, 0] - R[0, 1]) / s
            qx = (R[0, 2] + R[2, 0]) / s
            qy = (R[1, 2] + R[2, 1]) / s
            qz = 0.25 * s

    n = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    return (qx/n, qy/n, qz/n, qw/n)


def average_quaternions(quats: np.ndarray, weights: Optional[np.ndarray] = None) -> np.ndarray:
    """
    quats: (N,4) in (x,y,z,w)
    Markley method (eigenvector of weighted outer-products).
    """
    if quats.shape[0] == 1:
        q = quats[0].copy()
        return q / np.linalg.norm(q)

    if weights is None:
        weights = np.ones((quats.shape[0],), dtype=float)
    weights = weights / (np.sum(weights) + 1e-12)

    # hemisphere alignment to first quaternion
    ref = quats[0]
    Q = quats.copy()
    for i in range(Q.shape[0]):
        if np.dot(Q[i], ref) < 0:
            Q[i] = -Q[i]

    A = np.zeros((4, 4), dtype=float)
    for q, w in zip(Q, weights):
        A += w * np.outer(q, q)

    eigvals, eigvecs = np.linalg.eigh(A)
    q_avg = eigvecs[:, np.argmax(eigvals)]
    return q_avg / (np.linalg.norm(q_avg) + 1e-12)


def quaternion_to_rotation_matrix(q: np.ndarray) -> np.ndarray:
    qx, qy, qz, qw = q.tolist()
    n = math.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    qx, qy, qz, qw = qx/n, qy/n, qz/n, qw/n
    xx, yy, zz = qx*qx, qy*qy, qz*qz
    xy, xz, yz = qx*qy, qx*qz, qy*qz
    wx, wy, wz = qw*qx, qw*qy, qw*qz
    return np.array([
        [1 - 2*(yy+zz), 2*(xy-wz),     2*(xz+wy)],
        [2*(xy+wz),     1 - 2*(xx+zz), 2*(yz-wx)],
        [2*(xz-wy),     2*(yz+wx),     1 - 2*(xx+yy)]
    ], dtype=float)


# =========================
# shared memory (System V)
# =========================

SHM_MSG_KEY = 0x2387


class SHMmsgs(ctypes.Structure):
    _fields_ = [
        ("Status1", ctypes.c_uint16),
        ("Status2", ctypes.c_uint16),
        ("j_pos", ctypes.c_int16 * 16),
        ("j_tar", ctypes.c_int16 * 16),
        ("j_cur", ctypes.c_int16 * 16),
        ("j_kin", (ctypes.c_int16 * 3) * 4),
        ("j_tac", ctypes.c_int16 * 60),
        ("Denso_Status", ctypes.c_uint16),
        ("Denso_j_pos", ctypes.c_double * 6),
        ("Denso_j_tar", ctypes.c_double * 6),
        ("fd_usb", ctypes.c_int),
        ("Motorized_Stage_X", ctypes.c_int16),
        ("Motorized_Stage_Y", ctypes.c_int16),
        ("Camera_FPS", ctypes.c_double),
        ("Object_Pose", ctypes.c_double * 7),  # x, y, z, qx, qy, qz, qw
        ("process_num", ctypes.c_int),
    ]


def attach_shm() -> Optional[ctypes.POINTER(SHMmsgs)]:
    libc_path = ctypes.util.find_library("c")
    if not libc_path:
        print("[WARN] libc not found; shared memory disabled.")
        return None
    libc = ctypes.CDLL(libc_path, use_errno=True)
    shmget = libc.shmget
    shmat = libc.shmat
    shmget.argtypes = [ctypes.c_int, ctypes.c_size_t, ctypes.c_int]
    shmget.restype = ctypes.c_int
    shmat.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    shmat.restype = ctypes.c_void_p

    shm_id = shmget(SHM_MSG_KEY, ctypes.sizeof(SHMmsgs), 0o666)
    if shm_id < 0:
        err = ctypes.get_errno()
        print(f"[WARN] shmget failed (errno={err}); shared memory disabled.")
        return None
    addr = shmat(shm_id, None, 0)
    if addr in (0, ctypes.c_void_p(-1).value):
        err = ctypes.get_errno()
        print(f"[WARN] shmat failed (errno={err}); shared memory disabled.")
        return None
    print(f"[INFO] shared memory attached: key=0x{SHM_MSG_KEY:x}, shmid={shm_id}")
    return ctypes.cast(addr, ctypes.POINTER(SHMmsgs))


# =========================
# cube mount model (tag -> cube)
# =========================

@dataclass
class CubeFaceMount:
    tag_id: int
    T_tag_cube: np.ndarray  # 4x4


def generate_matrix_mounts(
    rows: int,
    cols: int,
    face_rpy_deg: Sequence[Tuple[float, float, float]],
    spacing: float,
    center_offset: float,
    base_tag_id: int,
) -> Dict[int, CubeFaceMount]:
    mounts: Dict[int, CubeFaceMount] = {}
    per_face = rows * cols

    for face_idx, (r_deg, p_deg, y_deg) in enumerate(face_rpy_deg[:FACE_COUNT]):
        # tag_to_cube rotation
        R = euler_xyz_to_matrix(math.radians(r_deg), math.radians(p_deg), math.radians(y_deg))
        # 위에서 만든 R은 "cube_to_tag"로 쓰는 경우도 많아서,
        # 여기서는 네 기존 코드와 동일하게 tag_to_cube = (cube_to_tag)^T 형태를 쓰고 싶으면 아래처럼 바꿀 수 있음.
        # 하지만 기본값이 네 세팅에 맞게 되어있어서 우선은 그대로 둠.
        R_tag_cube = R.T

        for row in range(rows):
            for col in range(cols):
                tag_id = base_tag_id + face_idx * per_face + row * cols + col

                # tag frame에서 cube center까지 translation (tag->cube)
                # x/y는 그리드 위치, z는 center_offset
                offset_x = ((cols - 1) * 0.5 - col) * spacing
                offset_y = ((rows - 1) * 0.5 - row) * spacing
                t_tag_cube = np.array([offset_x, offset_y, center_offset], dtype=float)

                T_tag_cube = rotation_translation_to_matrix(R_tag_cube, t_tag_cube)
                mounts[tag_id] = CubeFaceMount(tag_id=tag_id, T_tag_cube=T_tag_cube)

    return mounts


# =========================
# visualization helpers
# =========================

def draw_axes(img: np.ndarray, K: np.ndarray, T_cam_obj: np.ndarray, axis_len: float = 0.05) -> None:
    R, t = matrix_to_rt(T_cam_obj)
    rvec, _ = cv2.Rodrigues(R)
    tvec = t.reshape(3, 1)

    pts = np.float32([
        [0, 0, 0],
        [axis_len, 0, 0],
        [0, axis_len, 0],
        [0, 0, axis_len],
    ]).reshape(-1, 3)

    proj, _ = cv2.projectPoints(pts, rvec, tvec, K, None)
    proj = proj.reshape(-1, 2).astype(int)

    o = tuple(proj[0])
    cv2.line(img, o, tuple(proj[1]), (0, 0, 255), 2)   # X (red)
    cv2.line(img, o, tuple(proj[2]), (0, 255, 0), 2)   # Y (green)
    cv2.line(img, o, tuple(proj[3]), (255, 0, 0), 2)   # Z (blue)
    cv2.circle(img, o, 4, (0, 255, 255), -1)


# =========================
# main
# =========================

def main() -> None:
    # AprilTag detector
    detector = Detector(
        families=TAG_FAMILY,
        nthreads=2,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=True,
        decode_sharpening=0.25,
        debug=0,
    )

    mounts = generate_matrix_mounts(
        ROWS, COLS, DEFAULT_FACE_RPY_DEG, TAG_SPACING_M, CENTER_OFFSET_M, BASE_TAG_ID
    )
    target_ids = set(mounts.keys())

    # RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    profile = pipeline.start(config)

    color_stream = profile.get_stream(rs.stream.color).as_video_stream_profile()
    intr = color_stream.get_intrinsics()
    fx, fy, cx, cy = intr.fx, intr.fy, intr.ppx, intr.ppy
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0,  0,  1]], dtype=float)
    camera_params = (fx, fy, cx, cy)

    print("[INFO] RealSense started.")
    print(f"[INFO] intrinsics: fx={fx:.2f}, fy={fy:.2f}, cx={cx:.2f}, cy={cy:.2f}")
    print(f"[INFO] tracking tag IDs: {min(target_ids)} ~ {max(target_ids)} (count={len(target_ids)})")
    print("[INFO] press 'q' to quit.")

    shm_ptr = attach_shm()
    if shm_ptr is None:
        raise RuntimeError("Shared memory not available. Start the shm creator process first.")

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color = frames.get_color_frame()
            if not color:
                continue

            img = np.asanyarray(color.get_data())
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            detections = detector.detect(
                gray,
                estimate_tag_pose=True,
                camera_params=camera_params,
                tag_size=TAG_SIZE_M,
            )
            if not detections:
                cv2.imshow("realsense_apriltag_cube_pose", img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                continue

            # collect cube pose candidates
            cube_T_list: List[np.ndarray] = []
            dist_list: List[float] = []
            used_ids: List[int] = []

            for det in detections:
                tag_id = int(det.tag_id)
                if tag_id not in target_ids:
                    continue

                R_cam_tag = np.array(det.pose_R, dtype=float).reshape(3, 3)
                t_cam_tag = np.array(det.pose_t, dtype=float).reshape(3)
                T_cam_tag = rotation_translation_to_matrix(R_cam_tag, t_cam_tag)

                T_tag_cube = mounts[tag_id].T_tag_cube
                T_cam_cube = T_cam_tag @ T_tag_cube

                cube_T_list.append(T_cam_cube)
                dist_list.append(float(np.linalg.norm(t_cam_tag)))
                used_ids.append(tag_id)

                # draw tag outline + id
                corners = np.array(det.corners, dtype=int).reshape(4, 2)
                for i in range(4):
                    cv2.line(img, tuple(corners[i]), tuple(corners[(i + 1) % 4]), (0, 255, 0), 2)
                c = corners.mean(axis=0).astype(int)
                cv2.putText(img, f"ID {tag_id}", (c[0] + 5, c[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cube_pose_T: Optional[np.ndarray] = None
            if not hasattr(main, "_prev_cube_pose"):
                main._prev_cube_pose = None  # type: ignore[attr-defined]

            if cube_T_list:
                if POSE_MODE == "nearest":
                    idx = int(np.argmin(dist_list))
                    cube_pose_T = cube_T_list[idx]
                    used = [used_ids[idx]]
                else:
                    # fuse: weight 가까운 태그에 더 크게
                    d = np.array(dist_list, dtype=float)
                    w = 1.0 / (d + 1e-6)
                    w = w / (np.sum(w) + 1e-12)

                    # translation average
                    ts = np.stack([T[:3, 3] for T in cube_T_list], axis=0)
                    t_avg = np.sum(ts * w.reshape(-1, 1), axis=0)

                    # rotation average via quaternion
                    qs = np.stack([np.array(rotation_matrix_to_quaternion(T[:3, :3])) for T in cube_T_list], axis=0)
                    q_avg = average_quaternions(qs, w)

                    R_avg = quaternion_to_rotation_matrix(q_avg)

                    cube_pose_T = rotation_translation_to_matrix(R_avg, t_avg)
                    used = sorted(set(used_ids))

                # simple temporal smoothing to reduce jitter
                prev_T = main._prev_cube_pose  # type: ignore[attr-defined]
                if prev_T is not None:
                    prev_t = prev_T[:3, 3]
                    curr_t = cube_pose_T[:3, 3]
                    alpha_t = float(SMOOTH_TRANSLATION_ALPHA)
                    t_smooth = (1.0 - alpha_t) * prev_t + alpha_t * curr_t

                    prev_q = np.array(rotation_matrix_to_quaternion(prev_T[:3, :3]))
                    curr_q = np.array(rotation_matrix_to_quaternion(cube_pose_T[:3, :3]))
                    alpha_r = float(SMOOTH_ROTATION_ALPHA)
                    q_smooth = average_quaternions(
                        np.stack([prev_q, curr_q], axis=0),
                        np.array([1.0 - alpha_r, alpha_r], dtype=float),
                    )
                    R_smooth = quaternion_to_rotation_matrix(q_smooth)
                    cube_pose_T = rotation_translation_to_matrix(R_smooth, t_smooth)

                main._prev_cube_pose = cube_pose_T  # type: ignore[attr-defined]

                # draw cube axes
                draw_axes(img, K, cube_pose_T, axis_len=0.06)

                # print pose
                R_cube = cube_pose_T[:3, :3]
                t_cube = cube_pose_T[:3, 3]
                qx, qy, qz, qw = rotation_matrix_to_quaternion(R_cube)
                print(
                    f"[CUBE] used={used} "
                    f"t=[{t_cube[0]:.3f}, {t_cube[1]:.3f}, {t_cube[2]:.3f}] m "
                    f"q=[{qx:.3f}, {qy:.3f}, {qz:.3f}, {qw:.3f}]"
                )
                if shm_ptr is not None:
                    shm_ptr.contents.Object_Pose[:] = [t_cube[0], t_cube[1], t_cube[2], qx, qy, qz, qw]

            cv2.imshow("realsense_apriltag_cube_pose", img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()