import rclpy
import yaml
import time
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import Header
from geometry_msgs.msg import Pose
import numpy as np
from rclpy.node import Node
import subprocess

class MapSaver(Node):

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

class MapPub(Node):
    def __init__(self, resolution, map_width, map_height, map_vals, x_origin, y_origin):
        super().__init__('map_publisher')
        print("Node initialised")

        self.pub = self.create_publisher(OccupancyGrid, '/rad_map', 10)
        self.timer = self.create_timer(1.5, self.publish)  # Fixed typo in the method name

        self.prediction = map_vals
        self.map_width = map_width
        self.map_height = map_height
        self.resolution = resolution
        self.x_origin = x_origin
        self.y_origin = y_origin
        self.iteration = 1

    def publish(self):
        grid_size = (self.map_width, self.map_height)
        prediction_np = np.array(self.prediction)  # Convert prediction to a NumPy array
        image = prediction_np.reshape(grid_size)
        image = (image - image.min()) / (image.max() - image.min())
        image = (image * 100).astype(np.int64)
        image = image.T
        image = image.reshape(-1).tolist()  # Convert back to a list
        msg = OccupancyGrid()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = '/map'  # Set your frame_id here
        msg.info = OccupancyGrid().info
        msg.info.width = self.map_width
        msg.info.height = self.map_height
        msg.info.resolution = self.resolution
        msg.info.origin = Pose()
        msg.info.origin.position.x = self.x_origin
        msg.info.origin.position.y = self.y_origin
        msg.info.origin.position.z = 0.00
        msg.data = list(image)
        self.pub.publish(msg)
        print(f"published message {self.iteration}", end='\r')
        self.iteration += 1

def get_obs_map_values(txt_file_location):
    try:
        with open(txt_file_location, 'r') as file:
            obs_map_vals = [int(round(float(line.strip()), 4)) for line in file]
    except Exception as e:
        print(f"Error reading observation costmap file: {e}")
        obs_map_vals = []
    return obs_map_vals

def static_rad_sim(map_size, map_width, map_height):
    vals = [-1] * map_size
    vals_np = np.array(vals)  # Convert prediction to a NumPy array

    # Attempt reshaping
    try:
        image = vals_np.reshape((map_height, map_width))
    except ValueError as e:
        print("Error during reshape:", e)

    center = [map_height/2, map_width/2]
    amp = 10
    sigma = 20
    # This function replaces the actual simulated scalar field at the moment
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            image[x][y] = amp * np.exp(-((x - center[0])**2 + (y - center[1])**2) / (2 * sigma**2))
    
    image = (image - image.min()) / (image.max() - image.min())
    image = (image * 250).astype(np.int64)
    image = image.T
    image = image.reshape(-1).tolist()  # Convert back to a list
    
    return image

def get_map_metadata(yaml_file_location):
    with open(yaml_file_location, 'r') as file:
        yaml_data = yaml.safe_load(file)
        resolution = yaml_data["resolution"]
        origin = yaml_data["origin"]

    return float(resolution), origin

def get_map_size(pgm_file_location):
    with open(pgm_file_location, 'r', encoding='latin-1') as file:
        lines = file.readlines()

        # Extract the second line
        second_line = lines[1].strip()
        map_dimensions = second_line.split()

        width = map_dimensions[1]
        height = map_dimensions[0]

    return int(width), int(height)

def main(args=None):
    rclpy.init(args=args)
    # Set variables
    maps_location = './src/bunker_mini/maps/obs_costmap'
    map_metadata = get_map_metadata(maps_location + '.yaml')
    resolution = map_metadata[0]
    map_origin = map_metadata[1]
    map_origin_x = map_origin[0]
    map_origin_y = map_origin[1]
    map_dimensions = get_map_size(maps_location + '.pgm')
    map_width = map_dimensions[0]
    map_height = map_dimensions[1]
    map_size = map_width * map_height
    map_vals = static_rad_sim(map_size, map_width, map_height)

    map_publisher = MapPub(resolution, map_width, map_height, map_vals, map_origin_x, map_origin_y)
    map_saver = MapSaver()

    # rclpy.spin_once(map_saver)
    # time.sleep(2)
    rclpy.spin_once(map_publisher)
    print(f"Node spun")

    map_saver.destroy_node()
    map_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
