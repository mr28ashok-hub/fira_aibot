# Aibot Mapping & Voice Challenge Guide

This guide explains how to map your environment, tag rooms via voice, and then run the challenge.

## Phase 1: Mapping and Recording Room Locations

1. **Start the Robot:**
   ```bash
   roslaunch turtlebot3_bringup turtlebot3_robot.launch
   ```

2. **Start SLAM (Gmapping):**
   ```bash
   roslaunch turtlebot3_slam turtlebot3_slam.launch
   ```

3. **Start Voice Recognition:**
   ```bash
   roslaunch tb3_8gb fira_recognizer.launch
   ```

4. **Start the Point Recorder:**
   ```bash
   rosrun tb3_8gb point_recorder.py
   ```

5. **Record Rooms:**
   - Drive the robot to a room (e.g., NEURAL HUB).
   - Once inside, **say the room name clearly**.
   - The robot will announce "Recorded NEURAL HUB" and save the coordinates.
   - Repeat for all rooms and the start point.

6. **Save the Map:**
   ```bash
   rosrun map_server map_saver -f ~/map
   ```

---

## Phase 2: Running the Challenge

1. **Start Navigation:**
   ```bash
   roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=$HOME/map.yaml
   ```

2. **Start Voice Recognition:**
   ```bash
   roslaunch tb3_8gb fira_recognizer.launch
   ```

3. **Start the Challenge Logic:**
   ```bash
   rosrun tb3_8gb voice_challenge.py
   ```

---

## Available Room Names
- **SET A:** NEURAL HUB, VISION NODE, SENSOR GRID, RETURN TO START
- **SET B:** QUANTUM CORE, MOTION LINK, CONTROL BAY, GO TO START
