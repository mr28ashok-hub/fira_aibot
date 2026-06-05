# Aibot Mapping & Voice Challenge Guide

This guide explains how to map your environment, tag rooms manually for 100% reliability, and then run the challenge.

## Phase 1: Mapping and Recording Room Locations (Reliable Keyboard Version)

1. **Start the Robot:**
   \`\`\`bash
   roslaunch turtlebot3_bringup turtlebot3_robot.launch
   \`\`\`

2. **Start SLAM (Gmapping):**
   \`\`\`bash
   roslaunch turtlebot3_slam turtlebot3_slam.launch
   \`\`\`

3. **Start the Keyboard Recorder:**
   In a new terminal, run:
   \`\`\`bash
   rosrun tb3_8gb keyboard_recorder.py
   \`\`\`

4. **Tag Your Rooms:**
   Drive the robot to a spot and type the number in the **Keyboard Recorder** terminal:
   - Type **\"1\"** + Enter -> Tags **NEURAL HUB** and **QUANTUM CORE**
   - Type **\"2\"** + Enter -> Tags **VISION NODE** and **MOTION LINK**
   - Type **\"3\"** + Enter -> Tags **SENSOR GRID** and **CONTROL BAY**
   - Type **\"start\"** + Enter -> Tags **START POINTS** (Both Sets)

   *The robot will announce \"Room [X] recorded for both sets\" via Festival TTS.*

5. **Save the Map:**
   \`\`\`bash
   rosrun map_server map_saver -f ~/map
   \`\`\`

---

## Phase 2: Running the Challenge

1. **Start Navigation:**
   \`\`\`bash
   roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=\$HOME/map.yaml
   \`\`\`

2. **Start Voice Recognition:**
   \`\`\`bash
   roslaunch tb3_8gb fira_recognizer.launch
   \`\`\`

3. **Start the Challenge Logic:**
   \`\`\`bash
   rosrun tb3_8gb voice_challenge.py
   \`\`\`

---

## Command Reference
| Key Input | Tagged Rooms (Both Sets) |
| :--- | :--- |
| **1** | NEURAL HUB & QUANTUM CORE |
| **2** | VISION NODE & MOTION LINK |
| **3** | SENSOR GRID & CONTROL BAY |
| **start** | RETURN TO START & GO TO START |
