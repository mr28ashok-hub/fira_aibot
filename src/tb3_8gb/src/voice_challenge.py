#!/usr/bin/env python

import rospy
import actionlib
import yaml
import os
import subprocess
import time
import sys
import re
import select
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus

# Python 2/3 compatibility for input
if sys.version_info[0] >= 3:
    get_input = input
else:
    get_input = raw_input

class VoiceChallengeNode:
    def __init__(self):
        rospy.init_node('voice_challenge_node')

        self.locations_file = rospy.get_param('~locations_file', '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml')
        self.room_coordinates = {}
        self.load_locations()

        self.voice_command = ""
        self.selected_set = "NONE"
        self.allowed_commands = []
        self.visited_rooms = set()

        # Define Command Sets
        self.set_a = ["NEURAL HUB", "VISION NODE", "SENSOR GRID"]
        self.set_b = ["QUANTUM CORE", "MOTION LINK", "CONTROL BAY"]
        self.start_commands = ["RETURN TO START", "GO TO START"]
        self.common = ["CHECKPOINT 1"]

        self.voice_sub = rospy.Subscriber("/recognizer/output", String, self.voice_callback)
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("Waiting for move_base action server...")
        self.move_base.wait_for_server()

        self.select_set()

    def load_locations(self):
        try:
            if os.path.exists(self.locations_file):
                with open(self.locations_file, 'r') as f:
                    new_coords = yaml.safe_load(f) or {}
                if new_coords != self.room_coordinates:
                    self.room_coordinates = new_coords
        except Exception as e:
            rospy.logerr("Error loading locations: " + str(e))

    def say(self, text):
        rospy.loginfo("Announcing: " + text)
        try:
            p = subprocess.Popen(['festival', '--tts'], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
        except: pass

    def select_set(self):
        os.system('clear')
        print("\n" + "="*45)
        print("      FIRA VOICE CHALLENGE - MISSION START")
        print("="*45)
        print(" PLEASE SELECT YOUR SET IN THIS TERMINAL:")
        print(" 1. SET A (Neural Hub, Vision Node, Sensor Grid)")
        print(" 2. SET B (Quantum Core, Motion Link, Control Bay)")
        print("="*45)

        while not rospy.is_shutdown():
            try:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    choice = sys.stdin.readline().strip()
                    if choice == '1':
                        self.selected_set = "SET A"
                        self.allowed_commands = self.set_a + self.start_commands + self.common
                        self.active_rooms = self.set_a
                        break
                    elif choice == '2':
                        self.selected_set = "SET B"
                        self.allowed_commands = self.set_b + self.start_commands + self.common
                        self.active_rooms = self.set_b
                        break
            except EOFError:
                break

        self.say("Robot ready for " + self.selected_set)
        self.print_commands()

    def print_commands(self):
        os.system('clear')
        print("="*45)
        print("   ACTIVE MISSION: " + str(self.selected_set))
        print("="*45)
        print(" COMMANDS THE ROBOT WILL HEAR:")
        for cmd in self.allowed_commands:
            print(" >> " + cmd)
        print("="*45)
        print(" TYPE 'STOP' or 'CANCEL' here to abort navigation.")
        print("="*45)
        print(" Robot is listening... Say a command!\n")

    def voice_callback(self, msg):
        raw_cmd = msg.data.upper().strip()
        if not raw_cmd: return
        cmd = re.sub(' +', ' ', raw_cmd)
        if "CHECKPOINT ONE" in cmd: cmd = "CHECKPOINT 1"

        if cmd in self.allowed_commands:
            self.voice_command = cmd

    def send_goal(self, room_name):
        self.load_locations()
        if room_name not in self.room_coordinates:
            return False

        coords = self.room_coordinates[room_name]
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = float(coords['x'])
        goal.target_pose.pose.position.y = float(coords['y'])
        goal.target_pose.pose.orientation.z = float(coords['z'])
        goal.target_pose.pose.orientation.w = float(coords['w'])

        print("DEBUG: Sending goal to X: %.2f, Y: %.2f" % (coords['x'], coords['y']))
        self.move_base.send_goal(goal)

        # Monitor goal state and check for typed STOP/CANCEL
        while not rospy.is_shutdown():
            if self.move_base.wait_for_result(rospy.Duration(0.1)):
                break
            if select.select([sys.stdin], [], [], 0)[0]:
                typed = sys.stdin.readline().strip().upper()
                if typed in ["STOP", "CANCEL"]:
                    self.move_base.cancel_all_goals()
                    return False

        return self.move_base.get_state() == GoalStatus.SUCCEEDED

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            # Check for typed commands while idle
            if select.select([sys.stdin], [], [], 0)[0]:
                typed = sys.stdin.readline().strip().upper()
                if typed in ["STOP", "CANCEL"]:
                    self.move_base.cancel_all_goals()
                    self.say("Navigation stopped")
                    self.print_commands()

            if self.voice_command != "":
                cmd = self.voice_command
                self.voice_command = ""

                if cmd in self.room_coordinates:
                    self.say("Navigating to " + cmd)
                    if self.send_goal(cmd):
                        self.say("Reached " + cmd)

                        if cmd in self.active_rooms:
                            self.visited_rooms.add(cmd)
                            if len(self.visited_rooms) >= 3:
                                time.sleep(1)
                                self.say("ALL ROOM ENTERED. WHAT'S NEXT?")

                        if cmd in self.start_commands:
                            time.sleep(3)
                            self.say("ALL MISSION COMPLETED")
                    else:
                        if self.move_base.get_state() == GoalStatus.PREEMPTED:
                            self.say("Navigation stopped")
                        else:
                            self.say("Failed to reach " + cmd)
                    self.print_commands()
            rate.sleep()

if __name__ == '__main__':
    try:
        node = VoiceChallengeNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
