#!/usr/bin/env python3
"""
Franka Arm & Hand Target 전송 예제

predefined된 3개의 pose를 순서대로 전송
키보드 입력으로 1, 2, 3번 포즈 선택

사용법:
  python3 send_arm_target.py
  
  1 입력: 안전 포즈로 이동
  2 입력: 움직임 1로 이동
  3 입력: 움직임 2로 이동
  h 입력: Hand target 전송
  q 입력: 종료
"""

import subprocess
import sys

# ============================================
# Predefined Poses (7 joints, 단위: rad)
# ============================================

POSES = {
    1: {
        'name': '안전 포즈',
        'joints': [
            0.5578250288963318,
            -0.5940333604812622,
            0.741665780544281,
            -2.4347126483917236,
            -0.026700271293520927,
            1.1982516050338745,
            0.22571292519569397
        ]
    },
    2: {
        'name': '움직임 1',
        'joints': [
           0.5578250288963318,
            -0.5940333604812622,
            0.741665780544281,
            -2.4347126483917236,
            -1.05104624107480049,
            1.230082392692566,
            0.24696135520935059
        ]
    },
    3: {
        'name': '움직임 2',
        'joints': [
            0.6340193152427673,
            -0.6914846301078796,
            0.022211244329810143,
            -1.3714933395385742,
            -0.05104624107480049,
            1.230082392692566,
            0.24696135520935059
        ]
    },
}

# Hand Target 예제 (16개 조인트)
HAND_TARGETS = {
    'open': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 열린 상태
    'close': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],  # 닫힌 상태
    'half': [500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500],  # 반쯤
}


def send_target(pose_num: int):
    """ros2 topic pub으로 target 전송"""
    if pose_num not in POSES:
        print(f'❌ 잘못된 포즈 번호: {pose_num}')
        return False
    
    pose = POSES[pose_num]
    joints = pose['joints']
    
    # ros2 topic pub 명령어 생성
    joints_str = ', '.join([str(j) for j in joints])
    cmd = [
        'ros2', 'topic', 'pub', '--once',
        '/franka/arm_target/right',
        'kistar_hand_ros2/msg/FrankaArmTarget',
        f'{{joint_targets: [{joints_str}], arm_id: 0}}'
    ]
    
    print(f'📤 포즈 #{pose_num} ({pose["name"]}) 전송 중...')
    print(f'   joints: {[f"{j:.3f}" for j in joints]}')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f'✅ 전송 완료!')
            return True
        else:
            print(f'❌ 전송 실패: {result.stderr}')
            return False
    except subprocess.TimeoutExpired:
        print('❌ 타임아웃!')
        return False
    except Exception as e:
        print(f'❌ 에러: {e}')
        return False


def send_hand_target(joint_targets, duration=1.0):
    """Hand target 전송"""
    # ros2 topic pub 명령어 생성
    joints_str = ', '.join([str(j) for j in joint_targets])
    cmd = [
        'ros2', 'topic', 'pub', '--once',
        '/hand/target/right',
        'kistar_hand_ros2/msg/HandTarget',
        f'{{joint_targets: [{joints_str}], movement_duration: {duration}, hand_id: 0}}'
    ]
    
    print(f'📤 Hand Target 전송 중...')
    print(f'   joints: {joint_targets[:5]}... (처음 5개)')
    print(f'   duration: {duration}초')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f'✅ Hand Target 전송 완료!')
            return True
        else:
            print(f'❌ 전송 실패: {result.stderr}')
            return False
    except subprocess.TimeoutExpired:
        print('❌ 타임아웃!')
        return False
    except Exception as e:
        print(f'❌ 에러: {e}')
        return False


def send_both_targets(pose_num: int, hand_target_name: str, duration=1.0):
    """Arm과 Hand를 동시에 전송"""
    if pose_num not in POSES:
        print(f'❌ 잘못된 포즈 번호: {pose_num}')
        return False
    
    if hand_target_name not in HAND_TARGETS:
        print(f'❌ 잘못된 Hand target: {hand_target_name}')
        return False
    
    pose = POSES[pose_num]
    hand_targets = HAND_TARGETS[hand_target_name]
    
    print(f'📤 Arm + Hand 동시 전송 중...')
    print(f'   Arm 포즈: #{pose_num} ({pose["name"]})')
    print(f'   Hand: {hand_target_name}')
    
    # Arm 전송
    arm_success = send_target(pose_num)
    
    # Hand 전송
    hand_success = send_hand_target(hand_targets, duration)
    
    if arm_success and hand_success:
        print(f'✅ Arm + Hand 동시 전송 완료!')
        return True
    else:
        print(f'⚠️  일부 전송 실패 (Arm: {arm_success}, Hand: {hand_success})')
        return False


def print_menu():
    print()
    print('=' * 60)
    print('  Franka Arm & Hand Target Sender')
    print('=' * 60)
    print()
    print('  1️⃣  팔만 움직이기:')
    for num, pose in POSES.items():
        print(f'      {num}: {pose["name"]}')
    print()
    print('  2️⃣  핸드만 움직이기:')
    print('      h: Hand target 전송 (open/close/half 선택)')
    print()
    print('  3️⃣  둘다 동시에 움직이기:')
    print('      b: Arm + Hand 동시 전송')
    print()
    print('  q: 종료')
    print('=' * 60)
    print()


def main():
    print('🚀 Arm & Hand Target Sender 시작!')
    print_menu()
    
    try:
        while True:
            user_input = input('명령 입력 (1/2/3/h/b/q): ').strip()
            
            if user_input.lower() == 'q':
                print('👋 종료합니다.')
                break
            
            elif user_input.lower() == 'h':
                # Hand target만 선택
                print('\n  Hand Target 선택:')
                print('    o: open (열기)')
                print('    c: close (닫기)')
                print('    m: half (반쯤)')
                hand_choice = input('  선택 (o/c/m): ').strip().lower()
                
                if hand_choice == 'o':
                    send_hand_target(HAND_TARGETS['open'], 1.0)
                elif hand_choice == 'c':
                    send_hand_target(HAND_TARGETS['close'], 1.0)
                elif hand_choice == 'm':
                    send_hand_target(HAND_TARGETS['half'], 1.0)
                else:
                    print('❌ 잘못된 선택 (o/c/m)')
            
            elif user_input.lower() == 'b':
                # Arm + Hand 동시 전송
                print('\n  Arm 포즈 선택:')
                for num, pose in POSES.items():
                    print(f'    {num}: {pose["name"]}')
                try:
                    pose_num = int(input('  포즈 번호 (1/2/3): ').strip())
                    
                    print('\n  Hand Target 선택:')
                    print('    o: open (열기)')
                    print('    c: close (닫기)')
                    print('    m: half (반쯤)')
                    hand_choice = input('  선택 (o/c/m): ').strip().lower()
                    
                    hand_map = {'o': 'open', 'c': 'close', 'm': 'half'}
                    if hand_choice in hand_map:
                        send_both_targets(pose_num, hand_map[hand_choice], 1.0)
                    else:
                        print('❌ 잘못된 Hand 선택 (o/c/m)')
                except ValueError:
                    print('❌ 숫자를 입력하세요 (1, 2, 3)')
            
            else:
                # Arm만 전송
                try:
                    pose_num = int(user_input)
                    send_target(pose_num)
                except ValueError:
                    print('❌ 숫자를 입력하세요 (1, 2, 3) 또는 h/b/q')
                
    except KeyboardInterrupt:
        print('\n👋 종료합니다.')


if __name__ == '__main__':
    main()
