#!/usr/bin/env python

import rospy
import tf
import yaml
import os
from std_msgs.msg import String

class PointRecorder:
    def __init__(self):
        rospy.init_node('point_recorder')

        self.output_file = rospy.get_param('~output_file', '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml')
        self.room_data = {}

        # Load existing data if it exists
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.room_data = yaml.safe_load(f) or {}
            rospy.loginfo('Loaded existing room locations from ' + self.output_file)

        self.listener = tf.TransformListener()
        self.voice_sub = rospy.Subscriber('recognizer/output', String, self.voice_callback)

        # Mapping for short-form to long-form names
        self.short_mapping = {
            'HUB': 'NEURAL HUB',
            'NODE': 'VISION NODE',
            'GRID': 'SENSOR GRID',
            'CORE': 'QUANTUM CORE',
            'LINK': 'MOTION LINK',
            'BAY': 'CONTROL BAY',
            'START': 'START' # Special handling for start point
        }

        # Full list of recognized terms
        self.room_list = [
            'NEURAL HUB', 'VISION NODE', 'SENSOR GRID',
            'QUANTUM CORE', 'MOTION LINK', 'CONTROL BAY',
            'RETURN TO START', 'GO TO START'
        ]

        rospy.loginfo('Point Recorder Ready with Short-Form Support.')
        rospy.loginfo('Shortcuts: HUB, NODE, GRID, CORE, LINK, BAY, START')

    def voice_callback(self, msg):
        command = msg.data.upper().strip()
        rospy.loginfo('Heard: ' + command)

        matched_room = None

        # Check for shortcuts first
        if command in self.short_mapping:
            matched_room = self.short_mapping[command]
        else:
            # Fallback to long-form names
            for room in self.room_list:
                if room in command:
                    matched_room = room
                    break

        if matched_room:
            if matched_room == 'START':
                # Special case: Record both start point variations
                self.record_point('RETURN TO START')
                self.record_point('GO TO START')
            else:
                self.record_point(matched_room)

    def record_point(self, room_name):
        try:
            # Wait for the transform to be available
            self.listener.waitForTransform('/map', '/base_footprint', rospy.Time(0), rospy.Duration(1.0))
            (trans, rot) = self.listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))

            self.room_data[room_name] = {
                'x': float(trans[0]),
                'y': float(trans[1]),
                'z': float(rot[2]),
                'w': float(rot[3])
            }

            with open(self.output_file, 'w') as f:
                yaml.dump(self.room_data, f)

            rospy.loginfo('Recorded location for: ' + room_name)
            self.say('Recorded ' + room_name)

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
            rospy.logerr('Failed to get transform: ' + str(e))
            self.say('Failed to record ' + room_name)

    def say(self, text):
        import subprocess
        try:
            p = subprocess.Popen(['festival', '--tts'], stdin=subprocess.PIPE)
            p.communicate(input=text)
        except:
            pass

if __name__ == '__main__':
    recorder = PointRecorder()
    rospy.spin()
