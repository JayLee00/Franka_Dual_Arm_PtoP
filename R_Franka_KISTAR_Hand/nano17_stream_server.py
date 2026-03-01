#!/usr/bin/env python3
"""
Nano17 실시간 스트리밍 서버 (Windows)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- NI-DAQmx로 Dual Nano17 측정 → TCP로 Ubuntu PC에 전송
- Ubuntu에서 nano17_stream_client.py 실행 후, 이 서버 실행
- Ctrl+C 종료

※ 이 파일은 Windows PC에서 실행합니다 (NI-DAQmx + Nano17 필요)
"""
import json
import socket
import struct
import sys
import threading
import time
from pathlib import Path

import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration

# 프로젝트 루트에서 calibration 로드
_sys_path = Path(__file__).resolve().parent
if str(_sys_path) not in sys.path:
    sys.path.insert(0, str(_sys_path))
from calibration_FT28734 import CALIBRATION_MATRIX as CAL1, BIAS as BIAS1
from calibration_FT33988 import CALIBRATION_MATRIX as CAL2, BIAS as BIAS2

# ════════════════════════════════════════════════
#  설정
# ════════════════════════════════════════════════
DAQ_DEVICE = "Dev2"
SAMPLE_RATE = 1000
NANO1_CHANNELS = ["ai0", "ai1", "ai2", "ai3", "ai4", "ai5"]
NANO2_CHANNELS = ["ai6", "ai7", "ai16", "ai17", "ai18", "ai19"]
FT_LABELS = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]
ZEROING_SAMPLES = 500

# TCP 서버
HOST = "0.0.0.0"   # 모든 인터페이스에서 수신
PORT = 15556       # Nano17 스트리밍 포트

# 버퍼 전송: 이 샘플 수만큼 쌓았다가 한번에 전송 (지연 vs 부하 절충)
BATCH_SIZE = 50    # 50 samples @ 1kHz = 50ms 간격 전송
# BATCH_SIZE=1 이면 샘플마다 전송 (최저 지연, TCP 부하 ↑)


def pack_sample(t: float, n1: list, n2: list) -> bytes:
    """바이너리: 1 double(time) + 6 double(nano1) + 6 double(nano2) = 104 bytes"""
    return struct.pack("<13d", t, *n1, *n2)


def pack_batch_binary(samples: list) -> bytes:
    """바이너리 배치: [count:4] [sample0] [sample1] ..."""
    buf = struct.pack("<I", len(samples))
    for s in samples:
        buf += pack_sample(s["time"], s["nano1"], s["nano2"])
    return buf


def pack_batch_json(samples: list) -> bytes:
    """JSON 배치 (디버깅용, 상대적으로 느림)"""
    data = [
        {"t": s["time"], "n1": s["nano1"], "n2": s["nano2"]}
        for s in samples
    ]
    return (json.dumps(data) + "\n").encode("utf-8")


class Nano17StreamServer:
    def __init__(self, device: str = DAQ_DEVICE, sample_rate: int = SAMPLE_RATE):
        self.device = device
        self.sample_rate = sample_rate
        self._bias1 = BIAS1.copy()
        self._bias2 = BIAS2.copy()
        self._running = False
        self._daq_thread = None
        self._send_thread = None
        self._lock = threading.Lock()
        self._buffer: list = []
        self._conn: socket.socket | None = None
        self._client_addr = None
        self._use_binary = True  # True=바이너리, False=JSON

    def _channel_paths(self):
        return [f"{self.device}/{c}" for c in NANO1_CHANNELS + NANO2_CHANNELS]

    def measure_bias(self, n_samples: int = ZEROING_SAMPLES):
        print(f"[Zeroing] {n_samples} 샘플 측정 중...")
        channels = self._channel_paths()
        with nidaqmx.Task() as task:
            for ch in channels:
                task.ai_channels.add_ai_voltage_chan(
                    ch, min_val=-10.0, max_val=10.0,
                    terminal_config=TerminalConfiguration.DEFAULT,
                )
            task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.FINITE,
                samps_per_chan=n_samples,
            )
            task.start()
            data = task.read(number_of_samples_per_channel=n_samples, timeout=10.0)
        arr = np.asarray(data)
        self._bias1 = arr[0:6, :].mean(axis=1)
        self._bias2 = arr[6:12, :].mean(axis=1)
        print("[Zeroing] 완료")

    def _daq_loop(self):
        channels = self._channel_paths()
        chunk = max(1, int(self.sample_rate * 0.02))  # 20ms 청크

        with nidaqmx.Task() as task:
            for ch in channels:
                task.ai_channels.add_ai_voltage_chan(
                    ch, min_val=-10.0, max_val=10.0,
                    terminal_config=TerminalConfiguration.DEFAULT,
                )
            task.timing.cfg_samp_clk_timing(
                rate=self.sample_rate,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=self.sample_rate * 2,
            )
            t0 = time.perf_counter()
            while self._running:
                try:
                    data = task.read(number_of_samples_per_channel=chunk)
                    now = time.perf_counter() - t0
                    arr = np.asarray(data)
                    if arr.ndim == 2 and arr.shape[0] == 12:
                        for k in range(arr.shape[1]):
                            r1 = arr[0:6, k]
                            r2 = arr[6:12, k]
                            ft1 = (CAL1 @ (r1 - self._bias1)).tolist()
                            ft2 = (CAL2 @ (r2 - self._bias2)).tolist()
                            t = now + k / self.sample_rate
                            with self._lock:
                                self._buffer.append({"time": t, "nano1": ft1, "nano2": ft2})
                except Exception as e:
                    if self._running:
                        print(f"[DAQ] 오류: {e}")
                    break

    def _send_loop(self):
        while self._running:
            to_send = []
            with self._lock:
                n = min(BATCH_SIZE, len(self._buffer))
                if n > 0:
                    to_send = self._buffer[:n]
                    del self._buffer[:n]

            if to_send and self._conn:
                try:
                    if self._use_binary:
                        payload = pack_batch_binary(to_send)
                        # 길이 prefix (4 bytes) + payload
                        header = struct.pack("<I", len(payload))
                        self._conn.sendall(header + payload)
                    else:
                        payload = pack_batch_json(to_send)
                        self._conn.sendall(payload)
                except (BrokenPipeError, ConnectionResetError, OSError) as e:
                    print(f"[TCP] 전송 오류: {e}")
                    self._conn = None
            else:
                time.sleep(0.001)

    def run(self, host: str = HOST, port: int = PORT, auto_zero: bool = True):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        server.settimeout(1.0)

        print("=" * 60)
        print("  Nano17 스트리밍 서버 (Windows → Ubuntu)")
        print("=" * 60)
        print(f"  대기: 0.0.0.0:{port}")
        print("  Ubuntu에서 nano17_stream_client.py 실행 후 여기서 연결 수락")
        print("  Ctrl+C 종료")
        print("=" * 60)

        if auto_zero:
            self.measure_bias()

        # 클라이언트 연결 대기
        print("[TCP] Ubuntu 클라이언트 연결 대기 중...")
        try:
            conn, addr = server.accept()
            self._conn = conn
            self._client_addr = addr
            conn.settimeout(5.0)
            print(f"[TCP] 연결됨: {addr}")
        except Exception as e:
            print(f"[TCP] 연결 오류: {e}")
            server.close()
            return

        self._running = True
        self._daq_thread = threading.Thread(target=self._daq_loop, daemon=True)
        self._send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self._daq_thread.start()
        self._send_thread.start()
        print("[DAQ] 스트리밍 시작")

        try:
            while self._running and self._conn:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[종료] Ctrl+C")
        finally:
            self._running = False
            if self._daq_thread:
                self._daq_thread.join(timeout=2)
            if self._send_thread:
                self._send_thread.join(timeout=2)
            if self._conn:
                try:
                    self._conn.close()
                except Exception:
                    pass
            server.close()
            print("종료됨")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nano17 TCP 스트리밍 서버")
    parser.add_argument("--host", default=HOST, help="바인드 주소")
    parser.add_argument("--port", type=int, default=PORT, help="TCP 포트")
    parser.add_argument("--no-zero", action="store_true", help="zeroing 건너뛰기")
    args = parser.parse_args()

    server = Nano17StreamServer()
    try:
        server.run(host=args.host, port=args.port, auto_zero=not args.no_zero)
    except KeyboardInterrupt:
        pass
