#!/usr/bin/env python
import rospy
import tf
import yaml
import os

# Python 2/3 compatibility shim
try:
    input_func = raw_input
except NameError:
    input_func = input

class KeyboardRecorder:
    def __init__(self):
        rospy.init_node('keyboard_recorder')
        self.output_file = '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml'
        self.room_data = {}
        self.load_data()

        self.listener = tf.TransformListener()
        self.mapping = {
            'b': 'blue_pickup', 'r': 'red_pickup', 'y': 'yellow_pickup',
            '1': 'blue_dropoff', '2': 'red_dropoff', '3': 'yellow_dropoff',
            's': 'start', 'c': 'checkpoint'
        }
        self.print_menu()

    def load_data(self):
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r') as f:
                self.room_data = yaml.safe_load(f) or {}

    def save_data(self):
        with open(self.output_file, 'w') as f:
            yaml.dump(self.room_data, f)

    def print_menu(self):
        print('\n--- Challenge Coordinate Recorder ---')
        print('Record: [PICKUP] b/r/y | [DROPOFF] 1/2/3 | s:Start | c:Checkpoint (CP1)')
        print('Delete: type "del" then the key (e.g., "del c")')
        print('Quit: q')

    def record(self, key):
        if key not in self.mapping: return
        name = self.mapping[key]
        try:
            self.listener.waitForTransform('/map', '/base_footprint', rospy.Time(0), rospy.Duration(2.0))
            (trans, rot) = self.listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))
            self.room_data[name] = {'x': float(trans[0]), 'y': float(trans[1]), 'z': float(rot[2]), 'w': float(rot[3])}
            self.save_data()
            print('>>> SAVED: %s' % name.upper())
        except Exception as e:
            print('Error: %s' % e)

    def delete(self, key):
        if key not in self.mapping: return
        name = self.mapping[key]
        if name in self.room_data:
            del self.room_data[name]
            self.save_data()
            print('>>> DELETED: %s' % name.upper())

    def run(self):
        while not rospy.is_shutdown():
            cmd = input_func('Command: ').strip().lower()
            if cmd == 'q': break
            if cmd.startswith('del '):
                parts = cmd.split()
                if len(parts) > 1: self.delete(parts[1])
            else:
                self.record(cmd)

if __name__ == '__main__':
    KeyboardRecorder().run()
