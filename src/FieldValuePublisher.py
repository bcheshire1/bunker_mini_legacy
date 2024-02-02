#! /usr/bin/env python3
 
import rclpy
from rclpy.node import Node
import numpy as np
import time
 
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64
 
class FieldValuePublisher(Node):
    def __init__(self):
        super().__init__('get_field_value')
        print("Node initialized")
        self.declare_parameter('odom_topic', '/odom')  # Replace with your actual topic
        robot_odom = self.get_parameter('odom_topic').value
 
        # Subscribe to odom
        self.subscription = self.create_subscription(Odometry, robot_odom, self.pose_callback, 10)
 
        # Publish field - can also go
        self.publisher = self.create_publisher(Float64, 'field_value', 1)
 
    def get_field_value(self, x, y):
        # This function replaces the actual simulated scalar field at the moment
        center = [0.5, -0.4]
        amp = 2
        sigma = 1
        val = amp * np.exp(-((x - center[0])**2 + (y - center[1])**2) / (2 * sigma**2))
        # val = np.sin(x) + y
        return val
 
    def pose_callback(self, msg):
        pos_x = msg.pose.pose.position.x
        pos_y = msg.pose.pose.position.y
 
        val = self.get_field_value(pos_x, pos_y)
 
        # Publish field - can also go
        f = Float64()
        f.data = val
        self.publisher.publish(f)
        print(f'at position x:{round(pos_x, 2)}, y:{round(pos_y, 2)}, the field value is: {round(val, 7)}')
        time.sleep(1)
 
def main():
    rclpy.init()
    node = FieldValuePublisher()
    print(f"Starting to spin node...")
    rclpy.spin(node)
    print("Destroying node...")
    node.destroy_node()
    print("Shutting down node")
    rclpy.shutdown()
 
if __name__ == '__main__':
    main()