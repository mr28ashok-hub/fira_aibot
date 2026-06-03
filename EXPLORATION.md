# TurtleBot3 Autonomous SLAM Exploration

## Improvements for Map Accuracy
I identified that the original `gmapping_params.yaml` had a `linearUpdate` value of `1.0` and `angularUpdate` of `0.5`. This meant the robot would only update the map after moving 1 full meter or turning 28 degrees, which is too coarse for precise mapping and causes significant drift.

**Changes made:**
- Set `linearUpdate` to `0.1` (updates every 10cm).
- Set `angularUpdate` to `0.1` (updates every ~5 degrees).
- Adjusted `minimumScore` to `30` to allow better scan matching even with slightly noisy odometry.
- Reduced `particles` to `30` to maintain performance on the Raspberry Pi with more frequent updates.

## Autonomous Exploration Logic
The new node `tb3_exploration.py` provides simple autonomous movement:
1. It monitors LiDAR sectors (Front, Left, Right).
2. It moves forward at 0.15 m/s.
3. If an obstacle is detected within 0.5m in front, it automatically turns towards the direction with more open space.

## How to Launch
To start the autonomous mapping with a single command, run:
```bash
roslaunch tb3_8gb exploration.launch
```
*Note: Make sure your TurtleBot3 core and LiDAR are already running (`roslaunch turtlebot3_bringup turtlebot3_robot.launch`).*

## Saving the Map
Once you are satisfied with the map, open a new terminal and run:
```bash
rosrun map_server map_saver -f ~/my_new_map
```
