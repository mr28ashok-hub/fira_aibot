#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import time

class TB3Exploration:
    """
    Simple autonomous exploration node for TurtleBot3 using LiDAR.
    Moves forward and turns away from obstacles to explore and map.
    """
    def __init__(self):
        rospy.init_node('tb3_exploration')
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber('scan', LaserScan, self.scan_callback)
        self.twist = Twist()
        self.scan_data = None
        self.is_turning = False

    def scan_callback(self, data):
        self.scan_data = data

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if self.scan_data:
                # Basic obstacle avoidance logic for exploration
                # Frontal sector (around 0 degrees)
                front_ranges = self.scan_data.ranges[0:20] + self.scan_data.ranges[-20:]
                # Filter out zero values which often mean 'no hit' or 'out of range'
                valid_front = [r for r in front_ranges if r > 0.1]
                min_front = min(valid_front) if valid_front else 3.5

                # Left sector (around 45 degrees)
                left_ranges = self.scan_data.ranges[20:70]
                valid_left = [r for r in left_ranges if r > 0.1]
                min_left = min(valid_left) if valid_left else 3.5

                # Right sector (around 315 degrees)
                right_ranges = self.scan_data.ranges[290:340]
                valid_right = [r for r in right_ranges if r > 0.1]
                min_right = min(valid_right) if valid_right else 3.5

                if min_front < 0.5:
                    # Obstacle ahead, stop and turn
                    self.twist.linear.x = 0.0
                    if min_left > min_right:
                        self.twist.angular.z = 0.5 # Turn left
                    else:
                        self.twist.angular.z = -0.5 # Turn right
                    self.is_turning = True
                else:
                    if self.is_turning:
                        # Continue turning a bit more for clearing
                        rospy.sleep(1.0)
                        self.is_turning = False

                    self.twist.linear.x = 0.15
                    self.twist.angular.z = 0.0

                self.pub.publish(self.twist)
            rate.sleep()

if __name__ == '__main__':
    try:
        explorer = TB3Exploration()
        explorer.run()
    except rospy.ROSInterruptException:
        pass
