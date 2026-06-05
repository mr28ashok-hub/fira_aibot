# Catkin Workspace Analysis - tb3_8gb & SLAM

## Overview
This document analyzes the scripts in the `tb3_8gb` package for the TurtleBot3 and describes the implementation of autonomous SLAM exploration.

## Repository Structure
- `src/tb3_8gb/`: Contains the active source code, including the new `exploration.launch` and `tb3_exploration.py`.
- `src/turtlebot3/`: Contains the updated SLAM configurations for improved map accuracy.
- `backup_before_exploration/`: Contains the original state of the package as found on the Raspberry Pi before implementing the autonomous exploration.

## Existing Scripts Analysis

| Script | Purpose | Key Features |
| --- | --- | --- |
| `tb3_voice.py` | Teleop via voice | Controls `cmd_vel` based on commands: Stop, Forward, Backward, Left, Right. |
| `tb3_navvoice.py` | Basic navigation | Receives "back" and "move" commands to navigate to predefined points A and B. |
| `tb3_auto.py` | Obstacle avoidance | Uses LiDAR data (`/scan`) to navigate forward and turn away from obstacles. |
| `tb3_camshift.py` | Vision tracking | Uses `opencv_apps` to track an object/person by rotating the robot. |
| `voice_challenge.py`| FIRA Challenge | Handles sequential room navigation and voice commands. |
| `tb3_exploration.py`| Autonomous SLAM | Uses LiDAR to move independently and explore to build a map. |

## Autonomous SLAM Exploration Implementation

### Improved Map Accuracy:
The `gmapping_params.yaml` was updated with the following:
- `linearUpdate: 0.1` (was 1.0) - More frequent updates based on distance.
- `angularUpdate: 0.1` (was 0.5) - More frequent updates based on rotation.
- `minimumScore: 30` (was 50) - More robust scan matching.

### Autonomous Exploration Node:
`tb3_exploration.py` implements a wanderer algorithm that:
- Moves at 0.15 m/s.
- Detects obstacles within 0.5m in a 40-degree front arc.
- Chooses the direction with more open space (Left vs Right) to turn.

## How to Launch
To start the autonomous mapping with a single command:
```bash
roslaunch tb3_8gb exploration.launch
```
