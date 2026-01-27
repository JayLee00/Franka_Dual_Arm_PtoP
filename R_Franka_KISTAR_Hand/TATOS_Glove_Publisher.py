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
        
        self.serial_port = '/dev/ttyACM0'  # 포트 확인 필수
        self.baudrate = 115200
        
        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=0.1)
            # [중요 1] 시작할 때 버퍼에 쌓인 쓰레기 값을 비워줍니다.
            self.ser.reset_input_buffer()
            time.sleep(2) # 아두이노가 리셋 후 안정화될 때까지 대기
            self.get_logger().info(f'✅ Serial Connected & Buffer Cleared')
        except Exception as e:
            self.get_logger().error(f'❌ Connection Failed: {e}')
            exit(1)

        self.timer = self.create_timer(0.02, self.timer_callback)

    def timer_callback(self):
        if self.ser.in_waiting > 0:
            try:
                # [중요 2] 데이터 읽기
                raw_line = self.ser.readline()
                decoded_line = raw_line.decode('utf-8').strip()
                
                if not decoded_line:
                    return

                # [디버깅] 실제 들어오는 문자열 확인 (문제 해결 후 주석 처리)
                # 예: "Raw String: 0,4096,2000..." 이라고 떠야 정상
                self.get_logger().info(f'Raw String: {decoded_line}')

                values = list(map(int, decoded_line.split(',')))
                
                # 데이터가 12개가 맞는지 확인
                if len(values) == 12:
                    # [디버깅] 첫 번째 값(엄지)만 따로 출력해봅니다.
                    # self.get_logger().info(f'Thumb Val: {values[0]} | Full: {values}')
                    
                    full_targets = values + [0, 3000, 1000, 3000] 
                    
                    msg = HandTarget()
                    msg.joint_targets = full_targets
                    msg.movement_duration = 0.1 
                    msg.hand_id = 0
                    self.publisher_.publish(msg)
                    
                else:
                    self.get_logger().warn(f'⚠️ Size Mismatch: {len(values)} items received.')

            except ValueError:
                pass # 깨진 데이터 무시
            except Exception as e:
                self.get_logger().warn(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = GlovePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()