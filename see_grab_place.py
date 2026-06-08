#!/usr/bin/env python
import rospy
import cv2
import numpy as np
import time
import actionlib
import yaml
import os
import sys
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from sensor_msgs.msg import CompressedImage
from actionlib_msgs.msg import GoalStatus

# Python 2/3 compatibility for input
if sys.version_info[0] >= 3:
    get_input = input
else:
    get_input = raw_input

class SeeGrabPlace:
    def __init__(self):
        rospy.init_node('see_grab_place')
        self.locations_file = '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml'
        self.current_frame = None

        # Publisher for the gripper control node
        self.gripper_pub = rospy.Publisher('/gripper_cmd', String, queue_size=1)

        rospy.Subscriber('/raspicam_node/image/compressed', CompressedImage, self.image_callback)
        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)

        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base...")
        self.move_base.wait_for_server()
        rospy.loginfo("System Ready.")

    def image_callback(self, msg):
        np_arr = np.fromstring(msg.data, np.uint8)
        self.current_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def control_gripper(self, command):
        rospy.loginfo("Sending %s to gripper..." % command)
        self.gripper_pub.publish(command)
        rospy.sleep(2.0) # Wait for physical movement

    def detect_sign(self, timeout=30):
        rospy.loginfo("Scanning for sign (rotating)...")
        start = rospy.Time.now()
        twist = Twist(); twist.angular.z = 0.5
        # HSV ranges for Blue, Yellow, Red
        ranges = {
            'blue': ([100,150,50],[140,255,255]),
            'yellow': ([20,100,100],[30,255,255]),
            'red1': ([0,150,50],[10,255,255]),
            'red2': ([170,150,50],[180,255,255])
        }

        while (rospy.Time.now() - start).to_sec() < timeout and not rospy.is_shutdown():
            if self.current_frame is not None:
                hsv = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)
                for color in ['blue', 'yellow', 'red']:
                    if color == 'red':
                        mask = cv2.bitwise_or(cv2.inRange(hsv, np.array(ranges['red1'][0]), np.array(ranges['red1'][1])),
                                              cv2.inRange(hsv, np.array(ranges['red2'][0]), np.array(ranges['red2'][1])))
                    else:
                        mask = cv2.inRange(hsv, np.array(ranges[color][0]), np.array(ranges[color][1]))

                    if cv2.countNonZero(mask) > 5000: # Adjust threshold based on distance
                        rospy.loginfo("Seen: %s" % color)
                        self.cmd_vel_pub.publish(Twist()) # Stop
                        return color
            self.cmd_vel_pub.publish(twist)
            rospy.sleep(0.1)

        self.cmd_vel_pub.publish(Twist())
        return None

    def navigate_to(self, loc):
        if not os.path.exists(self.locations_file):
            rospy.logerr("Locations file %s missing!" % self.locations_file)
            return False
        with open(self.locations_file, 'r') as f:
            data = yaml.safe_load(f)
            if not data: return False
            coords = data.get(loc)

        if not coords:
            rospy.logerr("Location %s not found in room_locations.yaml!" % loc)
            return False

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = coords['x']
        goal.target_pose.pose.position.y = coords['y']
        goal.target_pose.pose.orientation.z = coords['z']
        goal.target_pose.pose.orientation.w = coords['w']

        rospy.loginfo("Navigating to %s..." % loc)
        self.move_base.send_goal(goal)
        self.move_base.wait_for_result()
        return self.move_base.get_state() == GoalStatus.SUCCEEDED

    def run(self):
        print("\n--- AiBOT See-Grab-Place Challenge 2026 ---")
        get_input("Ready? Press Enter to start mission: ")
        rospy.loginfo("Mission started.")

        # 1. Scan for Sign (SEE)
        color = self.detect_sign()
        if not color:
            rospy.logwarn("No sign found after timeout."); return

        # 2. Go to Pickup
        if self.navigate_to(color + "_pickup"):
            # 3. GRAB
            self.control_gripper("GRAB")

            # 4. Navigate through Checkpoint (Requirement)
            if self.navigate_to("checkpoint"):
                # 5. Go to Drop-off
                if self.navigate_to(color + "_dropoff"):
                    # 6. RELEASE
                    self.control_gripper("RELEASE")

                    # 7. Return to Start
                    self.navigate_to("start")
                    rospy.loginfo("MISSION COMPLETE.")
                else:
                    rospy.logerr("Failed to reach dropoff.")
            else:
                rospy.logerr("Failed to reach checkpoint.")
        else:
            rospy.logerr("Failed to reach pickup.")

if __name__ == '__main__':
    try:
        SeeGrabPlace().run()
    except rospy.ROSInterruptException:
        pass
