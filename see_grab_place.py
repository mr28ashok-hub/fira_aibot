#!/usr/bin/env python
import rospy
import cv2
import numpy as np
import serial
import time
import actionlib
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge
from actionlib_msgs.msg import GoalStatus

# --- Challenge Waypoints ---
TARGET_LOCATIONS = {
    'blue':   (1.606, 0.969, 0.0, 1.0), # MOTION LINK (x, y, z_orient, w_orient)
    'red':    (0.200, 1.000, 0.0, 1.0), # NEURAL HUB
    'yellow': (1.646, -0.389, 0.0, 1.0), # CONTROL BAY
}

# --- Detection Parameters ---
COLOUR_RANGES = {
    'blue':   ([100, 150, 50], [130, 255, 255]),
    'yellow': ([ 20, 150, 50], [ 35, 255, 255]),
    'red':    ([  0, 150, 50], [ 10, 255, 255]),
}

class SeeGrabPlace:
    def __init__(self):
        rospy.init_node('see_grab_place')
        self.bridge = CvBridge()
        self.current_frame = None
        self.ser = None

        # Initialize Serial for Gripper (Arduino)
        try:
            self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            rospy.loginfo("Connected to Gripper on /dev/ttyUSB0")
        except Exception as e:
            rospy.logerr("Failed to connect to gripper: %s" % e)

        # Subscribe to COMPRESSED image for performance and compatibility
        rospy.Subscriber('/raspicam_node/image/compressed', CompressedImage, self.image_callback)
        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)

        # MoveBase Client
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        self.move_base.wait_for_server()

        rospy.loginfo("System Ready for See-Grab-Place!")

    def image_callback(self, msg):
        try:
            np_arr = np.fromstring(msg.data, np.uint8)
            self.current_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except Exception as e:
            rospy.logerr("Image decode failed: %s" % e)

    def control_gripper(self, command):
        if self.ser:
            self.ser.write(command + "\n")
            rospy.loginfo("Sent to Arduino: %s" % command)
            time.sleep(1.5) # Wait for servo
            return True
        return False

    def detect_sign(self, timeout=30):
        rospy.loginfo("Scanning for signs...")
        start_time = rospy.Time.now()
        twist = Twist()
        twist.angular.z = 0.4

        while (rospy.Time.now() - start_time).to_sec() < timeout:
            if self.current_frame is not None:
                hsv = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)
                for color, (low, high) in COLOUR_RANGES.items():
                    mask = cv2.inRange(hsv, np.array(low), np.array(high))
                    count = cv2.countNonZero(mask)
                    if count > 1200: # Robust threshold
                        rospy.loginfo("DETECTED: %s Sign" % color.upper())
                        self.stop_robot()
                        return color

            self.cmd_vel_pub.publish(twist)
            rospy.sleep(0.1)

        self.stop_robot()
        return None

    def stop_robot(self):
        self.cmd_vel_pub.publish(Twist())
        rospy.sleep(0.5)

    def navigate_to(self, location_name):
        if location_name not in TARGET_LOCATIONS:
            return False

        rospy.loginfo("Navigating to %s waypoint..." % location_name)
        x, y, z_o, w_o = TARGET_LOCATIONS[location_name]

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = x
        goal.target_pose.pose.position.y = y
        goal.target_pose.pose.orientation.z = z_o
        goal.target_pose.pose.orientation.w = w_o

        self.move_base.send_goal(goal)
        self.move_base.wait_for_result(rospy.Duration(150))
        return self.move_base.get_state() == GoalStatus.SUCCEEDED

    def run(self):
        rospy.loginfo("Mission starts in 5 seconds. Place object in front of robot.")
        rospy.sleep(5)

        # 1. GRAB (Workpiece is in front at start)
        rospy.loginfo("Grabbing workpiece...")
        self.control_gripper("GRAB")

        # 2. SEE: Scan for a sign to know where to go
        detected_color = self.detect_sign()

        if detected_color:
            # 3. NAVIGATE: Go to the destination
            if self.navigate_to(detected_color):
                # 4. PLACE: Handover
                rospy.loginfo("Handoff position reached. Releasing...")
                self.control_gripper("RELEASE")
                rospy.loginfo("MISSION SUCCESSFUL.")
            else:
                rospy.logerr("Navigation failed.")
        else:
            rospy.logwarn("No sign detected. Aborting.")

if __name__ == '__main__':
    try:
        mission = SeeGrabPlace()
        mission.run()
    except rospy.ROSInterruptException:
        pass
