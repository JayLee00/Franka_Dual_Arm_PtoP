#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
import time
from kistar_hand_ros2.msg import HandTarget 

class GlovePublisher(Node):
    def __init__(self):
        super().__init__('glove_publisher_node')
        self.publisher_ = self.create_publisher(HandTarget, '/hand/target/right', 10)
        
        # ROS 파라미터로 포트와 보드레이트 설정 (기본값 지정)
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.serial_port = self.get_parameter('port').get_parameter_value().string_value
        self.baudrate = self.get_parameter('baudrate').get_parameter_value().integer_value
        
        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=0.1)
            # [중요 1] 시작할 때 버퍼에 쌓인 쓰레기 값을 비워줍니다.
            self.ser.reset_input_buffer()
            time.sleep(2) # 아두이노가 리셋 후 안정화될 때까지 대기
            self.ser.reset_input_buffer() # 대기 시간 동안 쌓인 데이터 다시 비우기
            self.get_logger().info(f'✅ Serial Connected & Buffer Cleared')
        except Exception as e:
            self.get_logger().error(f'❌ Connection Failed: {e}')
            exit(1)

        # 주기를 0.01(100Hz)로 높여 더 자주 확인합니다.
        self.timer = self.create_timer(0.01, self.timer_callback)

    def timer_callback(self):
        try:
            if self.ser is None or not self.ser.is_open:
                return

            # 버퍼에 데이터가 너무 많이 쌓여있으면(예: 500바이트 이상) 지연 방지를 위해 비웁니다.
            if self.ser.in_waiting > 500:
                self.ser.reset_input_buffer()
                self.get_logger().warn('🧹 Serial buffer overflow, clearing...')
        except (OSError, serial.SerialException) as e:
            self.get_logger().error(f'📡 Serial Port Error (Disconnected?): {e}')
            return

        last_msg = None
        
        # 버퍼에 있는 모든 라인을 읽어서 가장 마지막(최신) 것만 취합니다.
        while self.ser.in_waiting > 0:
            try:
                raw_line = self.ser.readline()
                decoded_line = raw_line.decode('utf-8').strip()
                
                if not decoded_line:
                    continue

                values = list(map(int, decoded_line.split(',')))
                
                if len(values) == 16 :
                    msg = HandTarget()
                    msg.joint_targets = values
                    msg.movement_duration = 0.1 
                    msg.hand_id = 0
                    last_msg = msg # 최신 메시지로 업데이트
                    last_msg = msg 
                else:
                    self.get_logger().warn(f'⚠️ Size Mismatch: {len(values)} items received.')
                    # 데이터가 잘린 경우(버퍼 리셋 직후 등) 발생할 수 있습니다.
                    self.get_logger().debug(f'⚠️ Size Mismatch: {len(values)} items. Expected 16.')

            except (UnicodeDecodeError, ValueError):
                self.get_logger().error('Parsing Error: Check Baudrate or Data Format')
                continue # 깨진 데이터는 무시하고 다음 라인 확인

        # 가장 최신 데이터 하나만 발행 (실시간성 확보)
        if last_msg:
            self.publisher_.publish(last_msg)
            # 성공적으로 발행되고 있는지 확인하려면 아래 주석을 해제하세요.
            # self.get_logger().info('Published latest hand target')

    def destroy_node(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            self.get_logger().info('Serial port closed.')
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = GlovePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard Interrupt (SIGINT)')
    except Exception as e:
        node.get_logger().error(f'Unexpected error: {e}')
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()

    ## 1. 현재 연결된 포트에 직접 권한 부여 (일시적)
#sudo chmod 666 /dev/ttyUSB0

# 2. 현재 사용자를 dialout 그룹에 추가 (영구적이나 재로그인 필요)
#sudo usermod -a -G dialout $USER

# 3. 현재 쉘 세션에 그룹 변경 사항 즉시 적용
#newgrp dialout

# udev 설정 후 실행 예시
#ython3 TATOS_Glove_Publisher.py
