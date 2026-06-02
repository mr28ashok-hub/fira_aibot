#!/bin/bash
sshpass -p 'turtlebot' ssh -p 40375 -o StrictHostKeyChecking=no pi@xhdzo-2402-1980-827-ffc1--1bb.run.pinggy-free.link "$@"
