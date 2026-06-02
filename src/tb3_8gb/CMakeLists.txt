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
