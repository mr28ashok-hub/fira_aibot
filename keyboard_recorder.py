#!/usr/bin/env python
import rospy
import tf
import yaml
import os

class KeyboardRecorder:
    def __init__(self):
        rospy.init_node('keyboard_recorder')
        self.output_file = '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml'
        self.room_data = {}
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.room_data = yaml.safe_load(f) or {}

        self.listener = tf.TransformListener()
        self.mapping = {
            'b': 'blue_pickup',
            'r': 'red_pickup',
            'y': 'yellow_pickup',
            '1': 'blue_dropoff',
            '2': 'red_dropoff',
            '3': 'yellow_dropoff',
            's': 'start'
        }
        print('--- Challenge Coordinate Recorder ---')
        print('Drive robot and type key to record:')
        print(" [PICKUP] 'b':Blue, 'r':Red, 'y':Yellow")
        print(" [DROPOFF] '1':Blue, '2':Red, '3':Yellow")
        print(" 's' for Start location")
        print(" 'q' to quit")

    def record(self, key):
        if key not in self.mapping: return
        name = self.mapping[key]
        try:
            self.listener.waitForTransform('/map', '/base_footprint', rospy.Time(0), rospy.Duration(2.0))
            (trans, rot) = self.listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))
            self.room_data[name] = {'x': float(trans[0]), 'y': float(trans[1]), 'z': float(rot[2]), 'w': float(rot[3])}
            with open(self.output_file, 'w') as f:
                yaml.dump(self.room_data, f)
            print('Saved: %s' % name.upper())
        except Exception as e:
            print('Error: %s' % e)

    def run(self):
        while not rospy.is_shutdown():
            user_input = raw_input('Key: ').strip().lower()
            if user_input == 'q': break
            self.record(user_input)

if __name__ == '__main__':
    KeyboardRecorder().run()
