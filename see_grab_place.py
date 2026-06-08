#!/usr/bin/env python
import rospy
import cv2
import numpy as np
import time
import actionlib
import yaml
import os
import sys
from std_srvs.srv import Empty
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
        np_arr = np.frombuffer(msg.data, np.uint8)
        self.current_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def control_gripper(self, command):
        rospy.loginfo("Sending %s to gripper..." % command)
        self.gripper_pub.publish(command)
        rospy.sleep(2.0) # Wait for physical movement

    def clear_costmaps(self):
        try:
            rospy.wait_for_service('/move_base/clear_costmaps', timeout=2.0)
            clear_costmaps = rospy.ServiceProxy('/move_base/clear_costmaps', Empty)
            clear_costmaps()
            rospy.loginfo("Costmaps cleared.")
        except Exception as e:
            rospy.logwarn("Could not clear costmaps: %s" % e)

    def navigate_to(self, loc):
        self.clear_costmaps()
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
        state = self.move_base.get_state()
        if state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Reached %s" % loc)
            return True
        else:
            rospy.logerr("Failed to reach %s. State: %s" % (loc, state))
            return False

    def execute_task(self, color):
        rospy.loginfo("--- Starting task for %s ---" % color.upper())

        # 1. Go to Pickup
        rospy.loginfo("Picking up %s" % color.upper())
        if not self.navigate_to(color + "_pickup"):
            rospy.logerr("Failed to reach %s pickup." % color)
            return False

        # 2. GRAB
        self.control_gripper("GRAB")

        # 3. Navigate through Checkpoint
        if not self.navigate_to("checkpoint"):
            rospy.logerr("Failed to reach checkpoint during %s task." % color)
            return False

        # 4. Go to Drop-off
        if not self.navigate_to(color + "_dropoff"):
            rospy.logerr("Failed to reach %s dropoff." % color)
            return False

        # 5. RELEASE
        self.control_gripper("RELEASE")
        return True

    def run(self):
        print("\n--- AiBOT See-Grab-Place Sequential Challenge ---")
        print("Sequence: BLUE -> RED -> YELLOW")
        get_input("Ready? Press Enter to start mission: ")
        rospy.loginfo("Mission started.")

        sequence = ['blue', 'red', 'yellow']

        for color in sequence:
            if not self.execute_task(color):
                rospy.logerr("Mission aborted at %s" % color)
                return

        # Return to Start
        rospy.loginfo("Returning to start position...")
        self.navigate_to("start")
        rospy.loginfo("FULL MISSION COMPLETE.")

if __name__ == '__main__':
    try:
        SeeGrabPlace().run()
    except rospy.ROSInterruptException:
        pass
