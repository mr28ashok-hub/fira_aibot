#!/usr/bin/env python
import rospy
import cv2
import numpy as np
import serial
import time
import actionlib
import yaml
import os
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from sensor_msgs.msg import CompressedImage
from actionlib_msgs.msg import GoalStatus

class SeeGrabPlace:
    def __init__(self):
        rospy.init_node('see_grab_place')
        self.locations_file = '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml'
        self.current_frame = None
        self.ser = None

        try:
            self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            rospy.loginfo("Gripper active.")
        except:
            rospy.logerr("Gripper failed.")

        rospy.Subscriber('/raspicam_node/image/compressed', CompressedImage, self.image_callback)
        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server()
        rospy.loginfo("System Ready.")

    def image_callback(self, msg):
        np_arr = np.fromstring(msg.data, np.uint8)
        self.current_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def control_gripper(self, command):
        if self.ser:
            self.ser.write(command + "\n")
            time.sleep(1.5)

    def detect_sign(self, timeout=20):
        rospy.loginfo("Scanning for sign...")
        start = rospy.Time.now()
        twist = Twist(); twist.angular.z = 0.4
        ranges = {'blue': ([100,150,50],[130,255,255]), 'yellow': ([20,150,50],[35,255,255]), 'red_1': ([0,150,50],[10,255,255]), 'red_2': ([170,150,50],[180,255,255])}
        while (rospy.Time.now() - start).to_sec() < timeout:
            if self.current_frame is not None:
                hsv = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)
                for color, (l, h) in [('blue', ranges['blue']), ('yellow', ranges['yellow']), ('red', ranges['red_1'])]:
                    mask = cv2.inRange(hsv, np.array(l), np.array(h))
                    if color == 'red': mask = cv2.bitwise_or(mask, cv2.inRange(hsv, np.array(ranges['red_2'][0]), np.array(ranges['red_2'][1])))
                    if cv2.countNonZero(mask) > 1200:
                        rospy.loginfo("Seen: %s" % color)
                        self.cmd_vel_pub.publish(Twist())
                        return color
            self.cmd_vel_pub.publish(twist); rospy.sleep(0.1)
        self.cmd_vel_pub.publish(Twist()); return None

    def navigate_to(self, loc):
        if not os.path.exists(self.locations_file): return False
        with open(self.locations_file, 'r') as f:
            data = yaml.safe_load(f)
            coords = data.get(loc)
        if not coords:
            rospy.logerr("Location %s not found!" % loc)
            return False
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = coords['x']
        goal.target_pose.pose.position.y = coords['y']
        goal.target_pose.pose.orientation.z = coords['z']
        goal.target_pose.pose.orientation.w = coords['w']
        self.move_base.send_goal(goal)
        self.move_base.wait_for_result()
        return self.move_base.get_state() == GoalStatus.SUCCEEDED

    def run(self):
        raw_input("Type 'start' to begin mission: ")
        rospy.loginfo("Mission started.")

        # 1. Scan for Sign (SEE)
        color = self.detect_sign()
        if not color:
            rospy.logwarn("No sign found."); return

        # 2. Go to Pickup
        rospy.loginfo("Heading to %s pickup..." % color)
        if self.navigate_to(color + "_pickup"):
            # 3. GRAB
            rospy.loginfo("Executing GRAB.")
            self.control_gripper("GRAB")

            # 4. TOUCH CHECKPOINT (CP1)
            rospy.loginfo("Heading to CHECKPOINT (CP1)...")
            if self.navigate_to("checkpoint"):
                rospy.loginfo("Checkpoint touched.")

                # 5. Go to Drop-off
                rospy.loginfo("Heading to %s drop-off..." % color)
                if self.navigate_to(color + "_dropoff"):
                    # 6. RELEASE
                    rospy.loginfo("Executing RELEASE.")
                    self.control_gripper("RELEASE")

                    # 7. Return to Start
                    rospy.loginfo("Returning to start.")
                    self.navigate_to("start")
                    rospy.loginfo("Mission Complete.")
                else:
                    rospy.logerr("Failed drop-off.")
            else:
                rospy.logerr("Failed checkpoint.")
        else:
            rospy.logerr("Failed pickup.")

if __name__ == '__main__':
    SeeGrabPlace().run()
