#!/usr/bin/env python3
"""
듀얼 전구 회전각 트래커: AprilTag 2개로 로봇/사람 전구 회전을 동시 측정.

카메라: Intel RealSense (640x480, 30fps)
태그:
  - tag ID 0 → 로봇 전구  (/bulb/angle)
  - tag ID 6 → 사람 전구  (/bulb/human_angle)

ROS2: --ros2 옵션 시 토픽 발행 + /bulb/reset 구독 (둘 다 동시 리셋)

'r' 키: 양쪽 누적각 동시 리셋 / 'q' 키: 종료
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np
import pyrealsense2 as rs
from pupil_apriltags import Detector


# ═══════════════ CONFIG ═══════════════
TAG_FAMILY = "tag36h11"
TAG_SIZE_M = 0.02
ROTATION_AXIS = "z"
ANGLE_SMOOTH_ALPHA = 0.5
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_FPS = 30

ROBOT_TAG_ID = 0
HUMAN_TAG_ID = 6

INFO_PANEL_H = 90  # 하단 정보 패널 높이 (px)


# ═══════════════ math utils ═══════════════

def rotation_matrix_to_euler_xyz(R: np.ndarray) -> tuple[float, float, float]:
    sy = math.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6
    if not singular:
        roll = math.atan2(R[2, 1], R[2, 2])
        pitch = math.atan2(-R[2, 0], sy)
        yaw = math.atan2(R[1, 0], R[0, 0])
    else:
        roll = math.atan2(-R[1, 2], R[1, 1])
        pitch = math.atan2(-R[2, 0], sy)
        yaw = 0.0
    return roll, pitch, yaw


def angle_diff(a: float, b: float) -> float:
    d = a - b
    while d > math.pi:
        d -= 2 * math.pi
    while d < -math.pi:
        d += 2 * math.pi
    return d


# ═══════════════ per-tag state ═══════════════

@dataclass
class TagState:
    tag_id: int
    label: str
    color: tuple  # BGR for drawing
    cumulative_deg: float = 0.0
    angular_velocity: float = 0.0
    prev_angle: Optional[float] = None
    smoothed_angle: Optional[float] = None
    tracking: bool = False

    def reset(self):
        self.cumulative_deg = 0.0
        self.angular_velocity = 0.0
        self.prev_angle = None
        self.smoothed_angle = None

    def update(self, det, axis_idx: int, dt: float):
        """AprilTag detection → 누적 회전 업데이트."""
        self.tracking = True
        R = np.array(det.pose_R, dtype=float).reshape(3, 3)
        angles = rotation_matrix_to_euler_xyz(R)
        current_angle = angles[axis_idx]

        if self.smoothed_angle is None:
            self.smoothed_angle = current_angle
        else:
            diff = angle_diff(current_angle, self.smoothed_angle)
            self.smoothed_angle += ANGLE_SMOOTH_ALPHA * diff

        if self.prev_angle is not None:
            delta = angle_diff(self.smoothed_angle, self.prev_angle)
            self.cumulative_deg += math.degrees(delta)
            if dt > 0:
                self.angular_velocity = math.degrees(delta) / dt
        self.prev_angle = self.smoothed_angle

    def decay(self):
        self.tracking = False
        self.angular_velocity *= 0.9


# ═══════════════ drawing helpers ═══════════════

def draw_tag_overlay(img, det, state: TagState):
    """태그 테두리 + 화살표 그리기."""
    corners = np.array(det.corners, dtype=int).reshape(4, 2)
    for i in range(4):
        cv2.line(img, tuple(corners[i]), tuple(corners[(i + 1) % 4]), state.color, 2)
    center = corners.mean(axis=0).astype(int)
    cv2.circle(img, tuple(center), 5, (0, 255, 255), -1)

    if state.smoothed_angle is not None and ROTATION_AXIS == "z":
        arrow_len = 50
        ax = int(center[0] + arrow_len * math.cos(state.smoothed_angle))
        ay = int(center[1] + arrow_len * math.sin(state.smoothed_angle))
        cv2.arrowedLine(img, tuple(center), (ax, ay), state.color, 2, tipLength=0.3)

    cv2.putText(img, f"ID{state.tag_id}", (corners[0][0], corners[0][1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, state.color, 1)


def draw_info_panel(img, robot: TagState, human: TagState):
    """영상 하단에 정보 패널을 그린다."""
    h, w = img.shape[:2]
    panel_y = h - INFO_PANEL_H
    cv2.rectangle(img, (0, panel_y), (w, h), (30, 30, 30), -1)
    cv2.line(img, (0, panel_y), (w, panel_y), (100, 100, 100), 1)
    mid_x = w // 2
    cv2.line(img, (mid_x, panel_y), (mid_x, h), (80, 80, 80), 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    y0 = panel_y + 22

    for i, st in enumerate([robot, human]):
        x_off = 10 if i == 0 else mid_x + 10
        status_str = "TRACKING" if st.tracking else "LOST"
        status_col = (0, 255, 0) if st.tracking else (0, 0, 255)

        cv2.putText(img, f"{st.label} (tag {st.tag_id})", (x_off, y0),
                    font, 0.5, st.color, 1)
        cv2.putText(img, status_str, (x_off + 200, y0),
                    font, 0.45, status_col, 1)

        angle_col = (0, 255, 0) if abs(st.cumulative_deg) < 360 else (0, 165, 255)
        cv2.putText(img, f"Angle: {st.cumulative_deg:+.1f} deg  ({st.cumulative_deg / 360:.2f} turns)",
                    (x_off, y0 + 25), font, 0.5, angle_col, 1)
        cv2.putText(img, f"Speed: {st.angular_velocity:+.1f} deg/s",
                    (x_off, y0 + 50), font, 0.5, (200, 200, 200), 1)


# ═══════════════ main ═══════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="듀얼 전구 회전각 트래커")
    parser.add_argument("--ros2", action="store_true", help="ROS2 토픽 발행")
    args, _ = parser.parse_known_args()

    # ── ROS2 ──
    ros2_node = None
    robot_pub = None
    human_pub = None
    Float64 = None

    if args.ros2:
        try:
            import rclpy
            from rclpy.node import Node
            from std_msgs.msg import Float64 as _Float64, Empty
            Float64 = _Float64
            rclpy.init()

            class DualBulbPublisher(Node):
                def __init__(self):
                    super().__init__('bulb_rotation_tracker')
                    self.robot_pub = self.create_publisher(Float64, '/bulb/angle', 10)
                    self.human_pub = self.create_publisher(Float64, '/bulb/human_angle', 10)
                    self.reset_requested = [False]
                    self.create_subscription(Empty, '/bulb/reset', self._cb_reset, 10)

                def _cb_reset(self, _msg):
                    self.reset_requested[0] = True

            ros2_node = DualBulbPublisher()
            robot_pub = ros2_node.robot_pub
            human_pub = ros2_node.human_pub
            ros2_node.get_logger().info(
                '/bulb/angle + /bulb/human_angle 발행, /bulb/reset 구독 활성화')
        except ImportError:
            print("[WARN] rclpy import 실패, ROS2 없이 실행합니다.")

    # ── AprilTag detector ──
    detector = Detector(
        families=TAG_FAMILY, nthreads=2, quad_decimate=1.0,
        quad_sigma=0.0, refine_edges=True, decode_sharpening=0.25, debug=0,
    )

    # ── RealSense ──
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, FRAME_WIDTH, FRAME_HEIGHT, rs.format.bgr8, FRAME_FPS)
    profile = pipeline.start(config)
    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    camera_params = (intr.fx, intr.fy, intr.ppx, intr.ppy)

    print(f"[INFO] RealSense: {FRAME_WIDTH}x{FRAME_HEIGHT}@{FRAME_FPS}fps")
    print(f"[INFO] Robot tag={ROBOT_TAG_ID}, Human tag={HUMAN_TAG_ID}, axis='{ROTATION_AXIS}'")
    print("[INFO] 'r'=reset both, 'q'=quit")

    axis_idx = {"x": 0, "y": 1, "z": 2}.get(ROTATION_AXIS, 2)

    robot = TagState(tag_id=ROBOT_TAG_ID, label="ROBOT", color=(0, 255, 0))
    human = TagState(tag_id=HUMAN_TAG_ID, label="HUMAN", color=(255, 165, 0))
    tag_states = {ROBOT_TAG_ID: robot, HUMAN_TAG_ID: human}

    prev_time = time.time()

    try:
        while True:
            # ROS2 리셋 처리
            if ros2_node is not None:
                rclpy.spin_once(ros2_node, timeout_sec=0)
                if ros2_node.reset_requested[0]:
                    robot.reset()
                    human.reset()
                    ros2_node.reset_requested[0] = False
                    print("[INFO] Both bulb angles reset (from /bulb/reset).")

            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            img = np.asanyarray(color_frame.get_data())
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            now = time.time()
            dt = now - prev_time
            prev_time = now

            detections = detector.detect(
                gray, estimate_tag_pose=True,
                camera_params=camera_params, tag_size=TAG_SIZE_M,
            )

            detected_ids = set()
            for det in detections:
                tid = int(det.tag_id)
                if tid in tag_states:
                    tag_states[tid].update(det, axis_idx, dt)
                    draw_tag_overlay(img, det, tag_states[tid])
                    detected_ids.add(tid)

            for tid, st in tag_states.items():
                if tid not in detected_ids:
                    st.decay()

            # 하단 정보 패널 (영상 확장)
            panel = np.full((INFO_PANEL_H, FRAME_WIDTH, 3), (30, 30, 30), dtype=np.uint8)
            canvas = np.vstack([img, panel])
            draw_info_panel(canvas, robot, human)

            # ROS2 발행 (매 프레임)
            if ros2_node is not None:
                msg_r = Float64()
                msg_r.data = robot.cumulative_deg
                robot_pub.publish(msg_r)
                msg_h = Float64()
                msg_h.data = human.cumulative_deg
                human_pub.publish(msg_h)

            cv2.imshow("Bulb Rotation Tracker", canvas)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                robot.reset()
                human.reset()
                print("[INFO] Both bulb angles reset.")

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        if ros2_node is not None:
            ros2_node.destroy_node()
            rclpy.shutdown()
        print(f"\n[RESULT] Robot: {robot.cumulative_deg:+.1f} deg  "
              f"Human: {human.cumulative_deg:+.1f} deg")


if __name__ == "__main__":
    main()
