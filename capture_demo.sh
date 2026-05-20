#!/usr/bin/env bash
# capture_demo.sh
# Runs a clean homebot session and captures the output for the README demo.
set +e

source /opt/ros/humble/setup.bash
source /root/homebot_ws/install/setup.bash

echo "=== Launching infrastructure (sensor_node + robot_simulator) ==="
ros2 launch homebot homebot.launch.py > /tmp/launch.log 2>&1 &
LAUNCH_PID=$!
sleep 5

echo
echo "=== ros2 topic list ==="
ros2 topic list | sort

echo
echo "=== Single sensor reading on /home/sensors/kitchen ==="
timeout 2 ros2 topic echo /home/sensors/kitchen --once 2>&1 | grep -E 'data:|---' | head -2

echo
echo "=== Sending: 'inspect the kitchen' ==="
ros2 run homebot task_dispatcher inspect the kitchen 2>&1 | grep -v -E 'INFO|WARN|^$' | head -10
sleep 1

echo
echo "=== Sending: 'check living room temperature' ==="
ros2 run homebot task_dispatcher check living room temperature 2>&1 | grep -v -E 'INFO|WARN|^$' | head -10
sleep 1

echo
echo "=== Sending: 'go to charging station' ==="
ros2 run homebot task_dispatcher go to charging station 2>&1 | grep -v -E 'INFO|WARN|^$' | head -10
sleep 1

echo
echo "=== Service call: /get_robot_position ==="
ros2 service call /get_robot_position std_srvs/srv/Trigger 2>&1 | tail -4

echo
echo "=== Cleanup ==="
pkill -f 'ros2 launch' 2>/dev/null
pkill -f 'sensor_node' 2>/dev/null
pkill -f 'robot_simulator' 2>/dev/null
sleep 1
echo DONE
