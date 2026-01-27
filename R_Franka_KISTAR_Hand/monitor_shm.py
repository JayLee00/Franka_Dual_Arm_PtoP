#!/usr/bin/env python3
"""
SHM (Shared Memory) 모니터링 스크립트
실시간으로 SHM에 쓰여지는 데이터를 모니터링합니다.

구조체 alignment를 고려하여 오프셋을 계산합니다.
"""

import sys
import ctypes
import struct
import time

# Linux 시스템 호출을 위한 ctypes 정의
libc = ctypes.CDLL('libc.so.6')

libc.shmget.argtypes = [ctypes.c_int, ctypes.c_size_t, ctypes.c_int]
libc.shmget.restype = ctypes.c_int

libc.shmat.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
libc.shmat.restype = ctypes.c_void_p

libc.shmdt.argtypes = [ctypes.c_void_p]
libc.shmdt.restype = ctypes.c_int

# SHM 키
SHM_KEY = 0x3940

# 상수 정의
Hand_Num = 2
Hand_DOF = 16
Kinesthetic_Sensor_DATA_NUM = 12
Tactile_Sensor_DATA_NUM = 60
Arm_Num = 2
Arm_DOF = 7

Hand_R = 0
Hand_L = 1
Arm_R = 0
Arm_L = 1


def align_offset(offset, alignment):
    """오프셋을 alignment에 맞게 조정"""
    if offset % alignment != 0:
        return offset + (alignment - (offset % alignment))
    return offset


class SHMMonitor:
    def __init__(self):
        self.shm_id = None
        self.shm_ptr = None
        self.shm_ptr_ctypes = None
        self.shm_size = 0
        
        # 오프셋 계산 (C++ 구조체 alignment 고려)
        self._calculate_offsets()
        
    def _calculate_offsets(self):
        """SHM 구조체의 각 필드 오프셋 계산"""
        offset = 0
        
        # uint16_t Motion_Sequence
        self.offset_Motion_Sequence = offset
        offset += 2
        
        # int16_t Hand_j_pos[2][16]
        self.offset_Hand_j_pos = offset
        offset += Hand_Num * Hand_DOF * 2
        
        # int16_t Hand_j_tar[2][16]
        self.offset_Hand_j_tar = offset
        offset += Hand_Num * Hand_DOF * 2
        
        # bool Hand_CMD_Status[2]
        self.offset_Hand_CMD_Status = offset
        offset += Hand_Num
        
        # 패딩 for double alignment (8 bytes)
        offset = align_offset(offset, 8)
        
        # double hand_movement_duration[2]
        self.offset_hand_movement_duration = offset
        offset += Hand_Num * 8
        
        # int16_t Hand_j_cur[2][16]
        self.offset_Hand_j_cur = offset
        offset += Hand_Num * Hand_DOF * 2
        
        # int16_t Hand_j_kin[2][12]
        self.offset_Hand_j_kin = offset
        offset += Hand_Num * Kinesthetic_Sensor_DATA_NUM * 2
        
        # int16_t Hand_j_tac[2][60]
        self.offset_Hand_j_tac = offset
        offset += Hand_Num * Tactile_Sensor_DATA_NUM * 2
        
        # uint8_t Hand_mode[2]
        self.offset_Hand_mode = offset
        offset += Hand_Num
        
        # uint8_t Hand_servo_on[2]
        self.offset_Hand_servo_on = offset
        offset += Hand_Num
        
        # 패딩 for int alignment (4 bytes)
        offset = align_offset(offset, 4)
        
        # std::array<int, 16> R_Hand_j_pos, R_Hand_j_cur, L_Hand_j_pos, L_Hand_j_cur
        self.offset_R_Hand_j_pos = offset
        offset += 16 * 4
        self.offset_R_Hand_j_cur = offset
        offset += 16 * 4
        self.offset_L_Hand_j_pos = offset
        offset += 16 * 4
        self.offset_L_Hand_j_cur = offset
        offset += 16 * 4
        
        # 패딩 for double alignment (8 bytes)
        offset = align_offset(offset, 8)
        
        # double Arm_j_pos[2][7]
        self.offset_Arm_j_pos = offset
        offset += Arm_Num * Arm_DOF * 8
        
        # double Arm_j_tar[2][7]
        self.offset_Arm_j_tar = offset
        offset += Arm_Num * Arm_DOF * 8
        
        # double Arm_j_vel[2][7]
        self.offset_Arm_j_vel = offset
        offset += Arm_Num * Arm_DOF * 8
        
        # double Arm_C_Pos[2][16]
        self.offset_Arm_C_Pos = offset
        offset += Arm_Num * 16 * 8
        
        # double Arm_j_tq[2][7]
        self.offset_Arm_j_tq = offset
        offset += Arm_Num * Arm_DOF * 8
        
        # franka::RobotState R_robot_state - 매우 큰 구조체, 건너뛰기
        # sizeof(franka::RobotState)는 약 2600-2800 bytes
        # 정확한 값은 컴파일러에 따라 다름
        self.offset_R_robot_state = offset
        FRANKA_ROBOT_STATE_SIZE = 2720  # 추정값, 필요시 조정
        offset += FRANKA_ROBOT_STATE_SIZE
        
        # std::array<double, 7> R_q
        self.offset_R_q = offset
        offset += 7 * 8
        
        # std::array<double, 7> R_qdes
        self.offset_R_qdes = offset
        offset += 7 * 8
        
        # std::array<double, 7> R_tau_d_last
        self.offset_R_tau_d_last = offset
        offset += 7 * 8
        
        # std::array<double, 7> R_gravity
        self.offset_R_gravity = offset
        offset += 7 * 8
        
        # franka::RobotState L_robot_state
        self.offset_L_robot_state = offset
        offset += FRANKA_ROBOT_STATE_SIZE
        
        # std::array<double, 7> L_q, L_qdes, L_tau_d_last, L_gravity
        self.offset_L_q = offset
        offset += 7 * 8
        self.offset_L_qdes = offset
        offset += 7 * 8
        self.offset_L_tau_d_last = offset
        offset += 7 * 8
        self.offset_L_gravity = offset
        offset += 7 * 8
        
        # gripper 관련 필드들... 생략
        
        print(f"📐 계산된 오프셋:")
        print(f"   Arm_j_pos: {self.offset_Arm_j_pos}")
        print(f"   Arm_j_tar: {self.offset_Arm_j_tar}")
        print(f"   Arm_j_tq: {self.offset_Arm_j_tq}")
        
    def connect(self):
        """SHM에 연결"""
        try:
            self.shm_id = libc.shmget(SHM_KEY, 0, 0)
            if self.shm_id == -1:
                print(f"❌ SHM을 찾을 수 없습니다 (키: 0x{SHM_KEY:x})")
                return False
            
            self.shm_ptr = libc.shmat(self.shm_id, None, 0)
            if self.shm_ptr == -1 or self.shm_ptr is None:
                print(f"❌ SHM attach 실패")
                return False
            
            self.shm_ptr_ctypes = ctypes.cast(self.shm_ptr, ctypes.POINTER(ctypes.c_uint8))
            
            # SHM 크기 확인
            class shmid_ds(ctypes.Structure):
                _fields_ = [
                    ("shm_perm", ctypes.c_byte * 48),
                    ("shm_segsz", ctypes.c_size_t),
                ]
            
            libc.shmctl.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(shmid_ds)]
            libc.shmctl.restype = ctypes.c_int
            
            shm_info = shmid_ds()
            if libc.shmctl(self.shm_id, 2, ctypes.byref(shm_info)) == 0:
                self.shm_size = shm_info.shm_segsz
                print(f"✅ SHM 연결 성공 (shm_id: {self.shm_id}, 크기: {self.shm_size} bytes)")
            
            return True
        except Exception as e:
            print(f"❌ SHM 연결 실패: {e}")
            return False
    
    def read_bytes(self, offset, size):
        return bytes((self.shm_ptr_ctypes[i] for i in range(offset, offset + size)))
    
    def read_double_array(self, offset, size):
        return struct.unpack(f'{size}d', self.read_bytes(offset, size * 8))
    
    def read_int16_array(self, offset, size):
        return struct.unpack(f'{size}h', self.read_bytes(offset, size * 2))
    
    def get_arm_data(self):
        """팔 데이터만 읽기"""
        data = {}
        
        # Arm_j_pos[2][7] - 직접 읽기
        data['Arm_j_pos'] = {}
        for a in range(Arm_Num):
            offset = self.offset_Arm_j_pos + a * Arm_DOF * 8
            data['Arm_j_pos'][a] = list(self.read_double_array(offset, Arm_DOF))
        
        # Arm_j_tar[2][7]
        data['Arm_j_tar'] = {}
        for a in range(Arm_Num):
            offset = self.offset_Arm_j_tar + a * Arm_DOF * 8
            data['Arm_j_tar'][a] = list(self.read_double_array(offset, Arm_DOF))
        
        # Arm_j_vel[2][7]
        data['Arm_j_vel'] = {}
        for a in range(Arm_Num):
            offset = self.offset_Arm_j_vel + a * Arm_DOF * 8
            data['Arm_j_vel'][a] = list(self.read_double_array(offset, Arm_DOF))
        
        # Arm_j_tq[2][7]
        data['Arm_j_tq'] = {}
        for a in range(Arm_Num):
            offset = self.offset_Arm_j_tq + a * Arm_DOF * 8
            data['Arm_j_tq'][a] = list(self.read_double_array(offset, Arm_DOF))
        
        return data
    
    def get_hand_data(self):
        """Hand 데이터 읽기"""
        data = {}
        
        # Hand_j_pos[2][16] - 현재 위치
        data['Hand_j_pos'] = {}
        for h in range(Hand_Num):
            offset = self.offset_Hand_j_pos + h * Hand_DOF * 2
            data['Hand_j_pos'][h] = list(self.read_int16_array(offset, Hand_DOF))
        
        # Hand_j_tar[2][16] - 목표 위치
        data['Hand_j_tar'] = {}
        for h in range(Hand_Num):
            offset = self.offset_Hand_j_tar + h * Hand_DOF * 2
            data['Hand_j_tar'][h] = list(self.read_int16_array(offset, Hand_DOF))
        
        # Hand_j_kin[2][12] - Kinesthetic 센서
        data['Hand_j_kin'] = {}
        for h in range(Hand_Num):
            offset = self.offset_Hand_j_kin + h * Kinesthetic_Sensor_DATA_NUM * 2
            data['Hand_j_kin'][h] = list(self.read_int16_array(offset, Kinesthetic_Sensor_DATA_NUM))

        # Hand_j_tac[2][60] - Tactile 센서
        data['Hand_j_tac'] = {}
        for h in range(Hand_Num):
            offset = self.offset_Hand_j_tac + h * Tactile_Sensor_DATA_NUM * 2
            data['Hand_j_tac'][h] = list(self.read_int16_array(offset, Tactile_Sensor_DATA_NUM))
        
        return data
    
    def print_summary(self, arm_data, hand_data):
        """데이터 요약 출력"""
        print("\n" + "="*80)
        print(f"📊 SHM 모니터링 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print(f"\n🤖 오른쪽 팔 (Arm_R):")
        print(f"  관절 위치 [rad]: {[f'{x:.4f}' for x in arm_data['Arm_j_pos'][Arm_R]]}")
        print(f"  관절 토크 [Nm]:  {[f'{x:.4f}' for x in arm_data['Arm_j_tq'][Arm_R]]}")
        print(f"  관절 속도 [rad/s]: {[f'{x:.4f}' for x in arm_data['Arm_j_vel'][Arm_R]]}")
        print(f"  목표 위치 [rad]: {[f'{x:.4f}' for x in arm_data['Arm_j_tar'][Arm_R]]}")
        
        print(f"\n✋ 오른쪽 손 (Hand_R):")
        print(f"  현재 조인트 각도: {hand_data['Hand_j_pos'][Hand_R]}")
        print(f"  목표 조인트 각도: {hand_data['Hand_j_tar'][Hand_R]}")
        print(f"  Kinesthetic 센서: {hand_data['Hand_j_kin'][Hand_R]}")
        print(f"  Tactile 센서:     {hand_data['Hand_j_tac'][Hand_R]}")
        
        print("\n" + "="*80)
    
    def monitor(self, interval=0.01):
        """SHM 모니터링 시작"""
        if not self.connect():
            return
        
        try:
            while True:
                arm_data = self.get_arm_data()
                hand_data = self.get_hand_data()
                self.print_summary(arm_data, hand_data)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  모니터링 중지됨")
        finally:
            if self.shm_ptr:
                libc.shmdt(self.shm_ptr)
            print("✅ SHM 연결 해제 완료")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='SHM 모니터링 스크립트')
    parser.add_argument('-i', '--interval', type=float, default=0.01, 
                       help='업데이트 간격 (초, 기본값: 0.5)')
    args = parser.parse_args()
    
    monitor = SHMMonitor()
    monitor.monitor(interval=args.interval)


if __name__ == '__main__':
    main()
