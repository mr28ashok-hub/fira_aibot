#!/usr/bin/env python

import rospy
import actionlib
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
import subprocess
import time

# Room Coordinates - To be adjusted based on the actual map
# Format: (x, y, z, w)
ROOM_COORDINATES = {
    # SET A
    "NEURAL HUB": (1.0, 0.0, 0.0, 1.0),
    "VISION NODE": (0.0, 1.0, 0.0, 1.0),
    "SENSOR GRID": (1.0, 1.0, 0.0, 1.0),
    "RETURN TO START": (0.0, 0.0, 0.0, 1.0),

    # SET B
    "QUANTUM CORE": (1.0, 0.0, 0.0, 1.0),
    "MOTION LINK": (0.0, 1.0, 0.0, 1.0),
    "CONTROL BAY": (1.0, 1.0, 0.0, 1.0),
    "GO TO START": (0.0, 0.0, 0.0, 1.0)
}

class VoiceChallengeNode:
    """
    ROS Node for the Aibot Voice Command Challenge.
    Handles sequential room navigation, voice commands, and status announcements.
    """
    def __init__(self):
        rospy.init_node('voice_challenge_node')

        self.voice_command = ""
        self.current_state = "WAITING_FOR_ROOM_1"
        self.rooms_visited = 0

        # Subscribers
        self.voice_sub = rospy.Subscriber("recognizer/output", String, self.voice_callback)

        # MoveBase Action Client
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        if not self.move_base.wait_for_server(rospy.Duration(30)):
            rospy.logerr("MoveBase server not available!")
            rospy.signal_shutdown("MoveBase server timeout")

        rospy.loginfo("Connected to move_base server")
        self.say("Robot ready for Voice Command Challenge")

    def say(self, text):
        """Announce status feedback via TTS."""
        rospy.loginfo("Announcing: " + text)
        try:
            # Use festival for TTS as verified on the Pi
            p = subprocess.Popen(['festival', '--tts'], stdin=subprocess.PIPE)
            p.communicate(input=text)
        except Exception as e:
            rospy.logerr("Failed to announce: %s", str(e))

    def voice_callback(self, msg):
        """Handle incoming voice commands from the recognizer."""
        self.voice_command = msg.data.upper()
        rospy.loginfo("Received voice command: " + self.voice_command)

    def send_goal(self, room_name):
        """Send a navigation goal to move_base."""
        if room_name not in ROOM_COORDINATES:
            rospy.logwarn("Room %s not found in coordinate map!", room_name)
            return False

        coords = ROOM_COORDINATES[room_name]
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position.x = coords[0]
        goal.target_pose.pose.position.y = coords[1]
        goal.target_pose.pose.orientation.z = coords[2]
        goal.target_pose.pose.orientation.w = coords[3]

        rospy.loginfo("Navigating to " + room_name)
        self.move_base.send_goal(goal)
        self.move_base.wait_for_result()

        if self.move_base.get_state() == GoalStatus.SUCCEEDED:
            rospy.loginfo("Reached " + room_name)
            return True
        else:
            rospy.logerr("Failed to reach %s. State: %s", room_name, str(self.move_base.get_state()))
            return False

    def run(self):
        """Main loop for the challenge state machine."""
        rate = rospy.Rate(10)
        room_list = ["NEURAL HUB", "VISION NODE", "SENSOR GRID", "QUANTUM CORE", "MOTION LINK", "CONTROL BAY"]

        while not rospy.is_shutdown():
            if self.current_state == "WAITING_FOR_ROOM_1":
                for room in room_list:
                    if room in self.voice_command:
                        if self.send_goal(room):
                            self.say("Reached first room. Stopping for 3 seconds.")
                            time.sleep(3)
                            self.rooms_visited = 1
                            self.current_state = "WAITING_FOR_ROOM_2"
                            self.voice_command = ""
                        break

            elif self.current_state == "WAITING_FOR_ROOM_2":
                for room in room_list:
                    if room in self.voice_command:
                        if self.send_goal(room):
                            self.say("Reached second room. Stopping for 3 seconds.")
                            time.sleep(3)
                            self.rooms_visited = 2
                            self.current_state = "WAITING_FOR_ROOM_3"
                            self.voice_command = ""
                        break

            elif self.current_state == "WAITING_FOR_ROOM_3":
                for room in room_list:
                    if room in self.voice_command:
                        if self.send_goal(room):
                            self.say("Reached third room. Stopping for 3 seconds.")
                            time.sleep(3)
                            self.rooms_visited = 3
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
                rospy.loginfo("Challenge completed.")
                break

            rate.sleep()

if __name__ == '__main__':
    try:
        node = VoiceChallengeNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
