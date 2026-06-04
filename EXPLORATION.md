# Aibot Mapping & Voice Challenge Guide

This guide explains how to map your environment, tag rooms via voice, and then run the challenge.

## Phase 1: Mapping and Recording Room Locations (Short-Form Commands)

1. **Start the Robot:**
   \`\`\`bash
   roslaunch turtlebot3_bringup turtlebot3_robot.launch
   \`\`\`

2. **Start SLAM (Gmapping):**
   \`\`\`bash
   roslaunch turtlebot3_slam turtlebot3_slam.launch
   \`\`\`

3. **Start Voice Recognition:**
   \`\`\`bash
   roslaunch tb3_8gb fira_recognizer.launch
   \`\`\`

4. **Start the Point Recorder:**
   \`\`\`bash
   rosrun tb3_8gb point_recorder.py
   \`\`\`

5. **Tag Rooms (FAST VERSION):**
   Drive the robot to a spot and say one of these short words:
   - **\"HUB\"** (for Neural Hub)
   - **\"NODE\"** (for Vision Node)
   - **\"GRID\"** (for Sensor Grid)
   - **\"CORE\"** (for Quantum Core)
   - **\"LINK\"** (for Motion Link)
   - **\"BAY\"** (for Control Bay)
   - **\"START\"** (for the Starting Point)

6. **Save the Map:**
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

## Recognized Commands Reference
| Room/Point | Voice Shortcut | Long-form Command |
| :--- | :--- | :--- |
| **Neural Hub** | **HUB** | \"NEURAL HUB\" |
| **Vision Node** | **NODE** | \"VISION NODE\" |
| **Sensor Grid** | **GRID** | \"SENSOR GRID\" |
| **Quantum Core** | **CORE** | \"QUANTUM CORE\" |
| **Motion Link** | **LINK** | \"MOTION LINK\" |
| **Control Bay** | **BAY** | \"CONTROL BAY\" |
| **Start Point** | **START** | \"RETURN/GO TO START\" |
