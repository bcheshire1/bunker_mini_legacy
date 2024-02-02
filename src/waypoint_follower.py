import rclpy
import time as t
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped


class PosePublisher(Node):

    def __init__(self):
        super().__init__('pose_publisher')
        self.publisher_ = self.create_publisher(PoseStamped, '/goal_pose', 10)
        timer_period = 1.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.x_pos = 3.0
        self.y_pos = 1.0
        self.z_pos = 0.0
        self.delta_x = -0.2
        self.delta_y = -0.1
        self.delta_z = 0.0

    def timer_callback(self):

        self.x_pos += self.delta_x
        self.y_pos += self.delta_y
        self.z_pos += self.delta_z

        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = 'map'
        pose_msg.pose.position.x = self.x_pos
        pose_msg.pose.position.y = self.y_pos
        pose_msg.pose.position.z = self.z_pos
        pose_msg.pose.orientation.x = 0.0
        pose_msg.pose.orientation.y = 0.0
        pose_msg.pose.orientation.z = 0.0
        pose_msg.pose.orientation.w = 1.0
        
        self.publisher_.publish(pose_msg)
        position_data = f'x: {pose_msg.pose.position.x}, y: {pose_msg.pose.position.y}'
        self.get_logger().info(f'Published PoseStamped message at position: {position_data}')


def main(args=None):
    rclpy.init(args=args)

    pose_publisher = PosePublisher()

    for i in range(10):
        rclpy.spin_once(pose_publisher)
        t.sleep(2)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    pose_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()