#!/usr/bin/env python3
"""
Nano17 스트리밍 클라이언트 (Ubuntu / Linux)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Windows nano17_stream_server.py에 TCP 연결
- 바이너리/JSON 수신 → 콘솔 출력 또는 ROS2 publish
- Ubuntu: pip install rclpy (ROS2 사용 시)

사용법:
  # ROS2 없이 수신만
  python3 nano17_stream_client.py --host 192.168.1.100

  # ROS2로 publish (Ubuntu with ROS2)
  python3 nano17_stream_client.py --host 192.168.1.100 --ros2
"""
import argparse
import socket
import struct
import sys
import threading
import time
from collections import deque

FT_LABELS = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
DEFAULT_PORT = 15556


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """정확히 n바이트 수신"""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("연결 종료")
        buf += chunk
    return buf


def parse_batch_binary(data: bytes) -> list:
    """서버 바이너리 형식 파싱: [count:4] [t, n1[6], n2[6]] * count"""
    samples = []
    pos = 0
    if len(data) < 4:
        return []
    count, = struct.unpack_from("<I", data, pos)
    pos += 4
    # 샘플당 13 doubles = 104 bytes
    for _ in range(count):
        if pos + 104 > len(data):
            break
        t, *rest = struct.unpack_from("<13d", data, pos)
        n1 = list(rest[:6])
        n2 = list(rest[6:12])
        samples.append({"time": t, "nano1": n1, "nano2": n2})
        pos += 104
    return samples


def parse_batch_with_length_prefix(sock: socket.socket) -> list:
    """4바이트 길이 prefix + payload 수신 후 파싱"""
    header = recv_exact(sock, 4)
    plen, = struct.unpack("<I", header)
    payload = recv_exact(sock, plen)
    return parse_batch_binary(payload)


def run_client(host: str, port: int, use_ros2: bool, print_interval: float, save_csv: str):
    print("=" * 60)
    print("  Nano17 스트리밍 클라이언트 (Ubuntu)")
    print("=" * 60)
    print(f"  연결: {host}:{port}")
    print("  Ctrl+C 종료")
    print("=" * 60)

    # ROS2 노드 (선택)
    ros2_node = None
    executor = None
    if use_ros2:
        try:
            import rclpy
            from rclpy.node import Node
            from rclpy.executors import SingleThreadedExecutor
            from geometry_msgs.msg import WrenchStamped
            from std_msgs.msg import Header

            class Nano17Ros2Bridge(Node):
                def __init__(self):
                    super().__init__("nano17_bridge")
                    self.pub1 = self.create_publisher(WrenchStamped, "/nano17/robot_hand", 10)
                    self.pub2 = self.create_publisher(WrenchStamped, "/nano17/tactile", 10)

                def publish(self, t: float, n1: list, n2: list):
                    h = Header()
                    h.stamp = self.get_clock().now().to_msg()
                    h.frame_id = "nano17"
                    w1 = WrenchStamped()
                    w1.header = h
                    w1.wrench.force.x, w1.wrench.force.y, w1.wrench.force.z = n1[0], n1[1], n1[2]
                    w1.wrench.torque.x, w1.wrench.torque.y, w1.wrench.torque.z = n1[3], n1[4], n1[5]
                    w2 = WrenchStamped()
                    w2.header = h
                    w2.wrench.force.x, w2.wrench.force.y, w2.wrench.force.z = n2[0], n2[1], n2[2]
                    w2.wrench.torque.x, w2.wrench.torque.y, w2.wrench.torque.z = n2[3], n2[4], n2[5]
                    self.pub1.publish(w1)
                    self.pub2.publish(w2)

            rclpy.init()
            ros2_node = Nano17Ros2Bridge()
            executor = SingleThreadedExecutor()
            executor.add_node(ros2_node)
        except ImportError as e:
            print(f"[ROS2] rclpy 미설치 또는 import 오류: {e}")
            print("  pip install rclpy (ROS2 환경에서)")
            use_ros2 = False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10.0)
    try:
        sock.connect((host, port))
    except (socket.timeout, OSError) as e:
        print(f"[연결 실패] {e}")
        print("  Windows 서버(nano17_stream_server.py)가 실행 중인지, IP/포트가 맞는지 확인")
        return 1
    sock.settimeout(2.0)
    print("[연결됨] 데이터 수신 중...")

    csv_file = None
    if save_csv:
        csv_file = open(save_csv, "w")
        csv_file.write("time,nano1_Fx,nano1_Fy,nano1_Fz,nano1_Tx,nano1_Ty,nano1_Tz,nano2_Fx,nano2_Fy,nano2_Fz,nano2_Tx,nano2_Ty,nano2_Tz\n")

    last_print = time.time()
    total_samples = 0
    running = True

    def spin_ros2():
        if use_ros2:
            while running and rclpy.ok():
                executor.spin_once(timeout_sec=0.05)

    if use_ros2:
        rt = threading.Thread(target=spin_ros2, daemon=True)
        rt.start()

    try:
        while True:
            try:
                batch = parse_batch_with_length_prefix(sock)
            except (ConnectionError, struct.error) as e:
                print(f"\n[연결 끊김] {e}")
                break

            for s in batch:
                total_samples += 1
                t, n1, n2 = s["time"], s["nano1"], s["nano2"]

                if csv_file:
                    row = f"{t},{','.join(str(x) for x in n1)},{','.join(str(x) for x in n2)}\n"
                    csv_file.write(row)

                if use_ros2 and ros2_node:
                    ros2_node.publish(t, n1, n2)

            now = time.time()
            if print_interval > 0 and (now - last_print) >= print_interval:
                fz1 = batch[-1]["nano1"][2] if batch else 0
                fz2 = batch[-1]["nano2"][2] if batch else 0
                print(f"  [Rx] {total_samples} samples | Fz: nano1={fz1:.3f} N, nano2={fz2:.3f} N")
                last_print = now

    except KeyboardInterrupt:
        print("\n[종료] Ctrl+C")
    finally:
        running = False
        if csv_file:
            csv_file.close()
            print(f"  CSV 저장: {save_csv}")
        sock.close()
        if use_ros2:
            rclpy.shutdown()

    print("종료됨")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Nano17 TCP 스트리밍 클라이언트 (Ubuntu)")
    parser.add_argument("--host", required=True, help="Windows PC IP (예: 192.168.1.100)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP 포트")
    parser.add_argument("--ros2", action="store_true", help="ROS2로 /nano17/robot_hand, /nano17/tactile publish")
    parser.add_argument("--print-interval", type=float, default=1.0, help="콘솔 출력 간격(초), 0=출력안함")
    parser.add_argument("--save-csv", default="", help="수신 데이터 CSV 저장 경로")
    args = parser.parse_args()

    return run_client(
        host=args.host,
        port=args.port,
        use_ros2=args.ros2,
        print_interval=args.print_interval,
        save_csv=args.save_csv,
    )


if __name__ == "__main__":
    sys.exit(main() or 0)
