# Catkin Workspace Analysis - tb3_8gb

## Overview
This document analyzes the scripts in the `tb3_8gb` package for the TurtleBot3 and describes the implementation of the "Voice Command Challenge" node.

## Repository Structure
- `src/tb3_8gb/`: Contains the active source code and the new challenge implementation.
- `backup/tb3_8gb/`: Contains the original state of the package as found on the Raspberry Pi.

## Existing Scripts Analysis

| Script | Purpose | Key Features |
| --- | --- | --- |
| `tb3_voice.py` | Teleop via voice | Controls `cmd_vel` based on commands: Stop, Forward, Backward, Left, Right. |
| `tb3_navvoice.py` | Basic navigation | Receives "back" and "move" commands to navigate to predefined points A and B using `move_base`. |
| `tb3_auto.py` | Obstacle avoidance | Uses LiDAR data (`/scan`) to navigate forward and turn away from obstacles. |
| `tb3_camshift.py` | Vision tracking | Uses `opencv_apps` to track an object/person by rotating the robot. |
| `tb3_navkey.py` | Keyboard navigation | Maps 'a' and 'b' keys to navigation goals. |

## Voice Command Challenge Implementation

The new node `voice_challenge.py` was created to automate the 5-task sequence required for the FIRA challenge.

### Requirements Fulfilled:
1. **Task 1-3**: Sequence of three room entries with 3-second stops at each.
2. **Task 4**: Return to start point on command.
3. **Task 5**: Announcement of "ALL MISSION COMPLETED" and final 3-second stop.
4. **Command Sets**: Support for both SET A and SET B room names.
5. **Feedback**: Status feedback via `festival` TTS for announcements.

### Implementation Details:
- **State Machine**: Managed via a Python class tracking `WAITING_FOR_ROOM_X` states.
- **Navigation**: Uses `actionlib` to communicate with the `move_base` action server.
- **Voice Parsing**: Listens to the `recognizer/output` topic for capitalized room names.
- **Safety**: Includes log warnings for unknown room names and error handling for failed navigation goals.
- **Announcements**: Uses `subprocess` to call `festival --tts` for robust audio feedback.

## Configuration
Room coordinates are currently defined as placeholders in `ROOM_COORDINATES` within `voice_challenge.py`. These must be tuned to the specific competition map.
