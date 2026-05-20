#!/usr/bin/env bash
# End-to-end smoke test for homebot.
set +e

source /opt/ros/humble/setup.bash
source /root/homebot_ws/install/setup.bash

echo "==> Launching infrastructure nodes in background..."
ros2 launch homebot homebot.launch.py > /tmp/launch.log 2>&1 &
LAUNCH_PID=$!

# Give nodes time to initialize and discover each other
sleep 5

echo ""
echo "==> ros2 topic list"
ros2 topic list | sort

echo ""
echo "==> ros2 service list (filtered)"
ros2 service list | grep -E 'robot|home' | sort

echo ""
echo "==> Dispatching task: 'inspect the kitchen'"
ros2 run homebot task_dispatcher inspect the kitchen > /tmp/dispatch.log 2>&1 &
DISP_PID=$!

sleep 4
echo "--- dispatcher log ---"
cat /tmp/dispatch.log

echo ""
echo "==> Calling service /get_robot_position"
ros2 service call /get_robot_position std_srvs/srv/Trigger 2>&1 | tail -6

echo ""
echo "==> Sample sensor reading from /home/sensors/kitchen (1 message)"
timeout 3 ros2 topic echo /home/sensors/kitchen --once 2>&1 | head -5

echo ""
echo "==> Launch log (last 15 lines)"
tail -15 /tmp/launch.log

echo ""
echo "==> Cleanup"
kill $DISP_PID 2>/dev/null
kill $LAUNCH_PID 2>/dev/null
pkill -f 'ros2 launch' 2>/dev/null
pkill -f 'sensor_node' 2>/dev/null
pkill -f 'robot_simulator' 2>/dev/null
pkill -f 'task_dispatcher' 2>/dev/null
sleep 1
echo "DONE"
