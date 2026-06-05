#!/usr/bin/env python

import rospy
import tf
import yaml
import os
import subprocess

class KeyboardRecorder:
    def __init__(self):
        rospy.init_node('keyboard_recorder')

        self.output_file = '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml'
        self.room_data = {}

        # Load existing data
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.room_data = yaml.safe_load(f) or {}

        self.listener = tf.TransformListener()

        self.mapping = {
            '1': ['NEURAL HUB', 'QUANTUM CORE'],
            '2': ['VISION NODE', 'MOTION LINK'],
            '3': ['SENSOR GRID', 'CONTROL BAY'],
            'start': ['RETURN TO START', 'GO TO START']
        }

        print("--- 100% Reliable Keyboard Recorder ---")
        print("Type '1', '2', '3', or 'start' and press Enter to tag current location.")
        print("Type 'q' to quit.")

    def say(self, text):
        try:
            p = subprocess.Popen(['festival', '--tts'], stdin=subprocess.PIPE)
            p.communicate(input=text)
        except: pass

    def record(self, key):
        if key not in self.mapping:
            print("Invalid input. Use 1, 2, 3, or start.")
            return

        rooms = self.mapping[key]
        try:
            self.listener.waitForTransform('/map', '/base_footprint', rospy.Time(0), rospy.Duration(1.0))
            (trans, rot) = self.listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))

            pose = {
                'x': float(trans[0]),
                'y': float(trans[1]),
                'z': float(rot[2]),
                'w': float(rot[3])
            }

            for room in rooms:
                self.room_data[room] = pose

            with open(self.output_file, 'w') as f:
                yaml.dump(self.room_data, f)

            msg = "Recorded " + ", ".join(rooms)
            print(msg)
            self.say("Room " + key + " recorded for both sets")

        except Exception as e:
            print("Error recording: " + str(e))

    def run(self):
        while not rospy.is_shutdown():
            user_input = raw_input("Input: ").strip().lower()
            if user_input == 'q':
                break
            self.record(user_input)

if __name__ == '__main__':
    recorder = KeyboardRecorder()
    recorder.run()
