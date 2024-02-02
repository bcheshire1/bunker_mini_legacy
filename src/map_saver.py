import rclpy
import numpy as np
import subprocess
from rclpy.node import Node

from nav_msgs.msg import OccupancyGrid


class MapSubscriber(Node):

    def __init__(self):
        super().__init__('map_subscriber')
        self.subscription = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_saver_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.file_location = './src/bunker_mini/maps/obs_costmap'

    def map_saver_callback(self, msg):
        # self.get_logger().info(f'The data received is: {msg.data}')
        np.savetxt(self.file_location + '.txt', msg.data)
        subprocess.run(['ros2', 'run', 'nav2_map_server', 'map_saver_cli', '-f', self.file_location])


def main(args=None):
    rclpy.init(args=args)

    map_subscriber = MapSubscriber()

    rclpy.spin_once(map_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    map_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()