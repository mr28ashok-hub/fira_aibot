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

        self.room_list = [
            'NEURAL HUB', 'VISION NODE', 'SENSOR GRID',
            'QUANTUM CORE', 'MOTION LINK', 'CONTROL BAY',
            'RETURN TO START', 'GO TO START'
        ]

        rospy.loginfo('Point Recorder Ready. Say a room name while mapping to record its location.')

    def voice_callback(self, msg):
        command = msg.data.upper()
        matched_room = None
        for room in self.room_list:
            if room in command:
                matched_room = room
                break

        if matched_room:
            self.record_point(matched_room)

    def record_point(self, room_name):
        try:
            # Wait for the transform to be available
            self.listener.waitForTransform('/map', '/base_footprint', rospy.Time(0), rospy.Duration(1.0))
            (trans, rot) = self.listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))

            self.room_data[room_name] = {
                'x': trans[0],
                'y': trans[1],
                'z': rot[2],
                'w': rot[3]
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
