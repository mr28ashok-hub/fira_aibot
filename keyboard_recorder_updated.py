#!/usr/bin/env python
import rospy
import tf
import yaml
import os
import sys

# Python 2/3 compatibility for input
if sys.version_info[0] >= 3:
    get_input = input
else:
    get_input = raw_input

class KeyboardRecorder:
    def __init__(self):
        rospy.init_node('keyboard_recorder')
        self.output_file = '/home/pi/catkin_ws/src/tb3_8gb/config/room_locations.yaml'
        self.room_data = {}
        self.load_data()
        self.listener = tf.TransformListener()
        # Mapping keys to lists of names to support Set A, Set B, and common names
        self.mapping = {
            '1': ['NEURAL HUB', 'QUANTUM CORE'],
            '2': ['VISION NODE', 'MOTION LINK'],
            '3': ['SENSOR GRID', 'CONTROL BAY'],
            's': ['RETURN TO START', 'GO TO START'],
            'c': ['CHECKPOINT 1', 'checkpoint']
        }
        self.print_menu()

    def load_data(self):
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    self.room_data = yaml.safe_load(f) or {}
            except Exception as e:
                print('Error loading YAML: %s' % e)
                self.room_data = {}

    def save_data(self):
        try:
            with open(self.output_file, 'w') as f:
                yaml.dump(self.room_data, f, default_flow_style=False)
        except Exception as e:
            print('Error saving YAML: %s' % e)

    def print_menu(self):
        print('\n--- Navigation Recorder (Python 2/3) ---')
        print('1: Room 1 (NEURAL HUB / QUANTUM CORE)')
        print('2: Room 2 (VISION NODE / MOTION LINK)')
        print('3: Room 3 (SENSOR GRID / CONTROL BAY)')
        print('s: START  (RETURN TO START / GO TO START)')
        print('c: CHECKPOINT (CHECKPOINT 1 / checkpoint)')
        print('del <key>: Delete mapping | q: Quit')

    def record(self, key):
        if key not in self.mapping:
            print('Invalid key: %s' % key)
            return

        names = self.mapping[key]
        try:
            self.listener.waitForTransform('/map', '/base_footprint', rospy.Time(0), rospy.Duration(2.0))
            (trans, rot) = self.listener.lookupTransform('/map', '/base_footprint', rospy.Time(0))

            coords = {
                'x': float(trans[0]),
                'y': float(trans[1]),
                'z': float(rot[2]),
                'w': float(rot[3])
            }

            for name in names:
                self.room_data[name] = coords

            self.save_data()
            print('>>> SAVED for: %s' % ', '.join(names))
        except Exception as e:
            print('Error recording: %s' % e)

    def delete(self, key):
        if key not in self.mapping:
            print('Invalid key for delete: %s' % key)
            return

        names = self.mapping[key]
        deleted = []
        for name in names:
            if name in self.room_data:
                del self.room_data[name]
                deleted.append(name)

        if deleted:
            self.save_data()
            print('>>> DELETED: %s' % ', '.join(deleted))
        else:
            print('>>> Nothing found to delete for key %s' % key)

    def run(self):
        while not rospy.is_shutdown():
            try:
                cmd = get_input('\nEnter Key/Command: ').strip().lower()
            except EOFError:
                break

            if cmd == 'q':
                break
            elif cmd.startswith('del '):
                parts = cmd.split()
                if len(parts) > 1:
                    self.delete(parts[1])
            elif cmd == 'm':
                self.print_menu()
            elif cmd:
                self.record(cmd)

if __name__ == '__main__':
    try:
        KeyboardRecorder().run()
    except rospy.ROSInterruptException:
        pass
