cmake_minimum_required(VERSION 3.0.2)
project(tb3_8gb)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  actionlib
  move_base_msgs
)

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS
  src/tb3_auto.py
  src/tb3_camshift.py
  src/tb3_navkey.py
  src/tb3_navvoice.py
  src/tb3_voice.py
  src/voice_challenge.py
  src/keyboard_recorder.py
  src/recognizer.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
