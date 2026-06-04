#!/usr/bin/env python

import rospy
import actionlib
import yaml
import os
import subprocess
import time
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus

class VoiceChallengeNode:
    def __init__(self):
        rospy.init_node('voice_challenge_node')

        self.locations_file = rospy.get_param('~locations_file', '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml')
        self.room_coordinates = {}
        self.load_locations()

        self.voice_command = ""
        self.current_state = "WAITING_FOR_ROOM_1"

        self.voice_sub = rospy.Subscriber("recognizer/output", String, self.voice_callback)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("Waiting for move_base...")
        self.move_base.wait_for_server()
        self.say("Robot ready for Voice Command Challenge")

    def load_locations(self):
        if os.path.exists(self.locations_file):
            with open(self.locations_file, 'r') as f:
                self.room_coordinates = yaml.safe_load(f) or {}
            rospy.loginfo("Loaded locations: " + str(self.room_coordinates.keys()))
        else:
            rospy.logwarn("Locations file not found! Please run point_recorder.py first.")

    def say(self, text):
        rospy.loginfo("Announcing: " + text)
        try:
            p = subprocess.Popen(['festival', '--tts'], stdin=subprocess.PIPE)
            p.communicate(input=text)
        except: pass

    def voice_callback(self, msg):
        self.voice_command = msg.data.upper()

    def send_goal(self, room_name):
        if room_name not in self.room_coordinates:
            rospy.logwarn("Room %s not found!", room_name)
            return False

        coords = self.room_coordinates[room_name]
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
        rate = rospy.Rate(10)
        room_list = ["NEURAL HUB", "VISION NODE", "SENSOR GRID", "QUANTUM CORE", "MOTION LINK", "CONTROL BAY"]

        while not rospy.is_shutdown():
            # Refresh locations in case they were updated
            self.load_locations()

            if self.current_state == "WAITING_FOR_ROOM_1":
                for room in room_list:
                    if room in self.voice_command:
                        if self.send_goal(room):
                            self.say("Reached first room. Stopping for 3 seconds.")
                            time.sleep(3)
                            self.current_state = "WAITING_FOR_ROOM_2"
                            self.voice_command = ""
                        break

            elif self.current_state == "WAITING_FOR_ROOM_2":
                for room in room_list:
                    if room in self.voice_command:
                        if self.send_goal(room):
                            self.say("Reached second room. Stopping for 3 seconds.")
                            time.sleep(3)
                            self.current_state = "WAITING_FOR_ROOM_3"
                            self.voice_command = ""
                        break

            elif self.current_state == "WAITING_FOR_ROOM_3":
                for room in room_list:
                    if room in self.voice_command:
                        if self.send_goal(room):
                            self.say("Reached third room. Stopping for 3 seconds.")
                            time.sleep(3)
                            self.say("ALL ROOM ENTERED. WHAT'S NEXT?")
                            self.current_state = "WAITING_FOR_START"
                            self.voice_command = ""
                        break

            elif self.current_state == "WAITING_FOR_START":
                if "RETURN TO START" in self.voice_command or "GO TO START" in self.voice_command:
                    start_cmd = "RETURN TO START" if "RETURN TO START" in self.voice_command else "GO TO START"
                    if self.send_goal(start_cmd):
                        self.say("Reached start point. Stopping for 3 seconds.")
                        time.sleep(3)
                        self.say("ALL MISSION COMPLETED")
                        self.current_state = "FINISHED"
                        self.voice_command = ""

            elif self.current_state == "FINISHED":
                break

            rate.sleep()

if __name__ == '__main__':
    node = VoiceChallengeNode()
    node.run()
