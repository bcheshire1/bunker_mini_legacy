import rospy
import numpy as np

from nav_msgs.msg import OccupancyGrid

def publish(self,prediction,lower_bound,upper_bound):
        grid_size=(self.resolution,self.resolution)
        image=prediction.view(grid_size)
 
        image=(image - image.min())/(image.max()-image.min())
        image=(image*100).int()
 
        image=image.t()
 
        image=image.reshape(-1).numpy()
 
        msg=OccupancyGrid()
        msg.header.stamp=rospy.Time.now()
        msg.header.frame_id = 'meepo_tf/map'
        #msg.header.frame_id = 'world'
        msg.info.width = self.resolution
        msg.info.height = self.resolution
        msg.info.resolution = (np.abs(upper_bound-lower_bound)) / self.resolution
 
        center_x = (lower_bound + upper_bound) / 2
        center_y = (lower_bound + upper_bound) / 2
        
        msg.info.origin.position.x=lower_bound
        msg.info.origin.position.y=lower_bound
        msg.info.origin.position.z=0
 
        msg.data = list(image)
        #print('here')
        self.pub.publish(msg)
        rospy.sleep(1)