# Robot Bash Aliases
# Restored on: 2026-06-09

alias cm='catkin_make -C ~/catkin_ws'
alias st='source ~/catkin_ws/devel/setup.bash'
alias so='source /opt/ros/kinetic/setup.bash'
alias bu='roslaunch turtlebot3_bringup turtlebot3_robot.launch'
alias sm='roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping'
alias lm="roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=/home/pi/map.yaml open_rviz:=true"
alias ms='rosrun map_server map_saver -f ~/map'
alias rc='rosrun tb3_8gb keyboard_recorder.py'
alias voice='rosrun tb3_8gb keyboard_recorder.py'
alias listen='roslaunch tb3_8gb fira_recognizer.launch'
alias challenge='rosrun tb3_8gb voice_challenge.py'
alias grab='roslaunch tb3_8gb see_grab_place.launch'
