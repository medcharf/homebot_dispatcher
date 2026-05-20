#!/usr/bin/env bash
# setup_wsl.sh
# ------------
# One-shot setup for WSL2 Ubuntu 22.04.
# Copies the project into ~/homebot_ws, builds it with colcon,
# and prints the next-step commands.
#
# Run from inside WSL Ubuntu:
#   cd /mnt/c/Users/charf/Downloads/ROS2/homebot_ws
#   bash setup_wsl.sh

set -e

PROJECT_SRC="/mnt/c/Users/charf/Downloads/ROS2/homebot_ws"
TARGET_WS="$HOME/homebot_ws"

echo "==> Checking prerequisites..."

if ! command -v ros2 >/dev/null 2>&1; then
    echo "ROS2 is not installed. Install ROS2 Humble first:"
    echo "  https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html"
    exit 1
fi

if ! command -v colcon >/dev/null 2>&1; then
    echo "colcon is not installed. Install with:"
    echo "  sudo apt install python3-colcon-common-extensions"
    exit 1
fi

echo "==> Copying project from $PROJECT_SRC to $TARGET_WS..."
mkdir -p "$TARGET_WS"
# Copy src/, README.md, .gitignore - skip build/install/log if they exist
rsync -a --exclude 'build' --exclude 'install' --exclude 'log' \
    --exclude '__pycache__' --exclude '.pytest_cache' \
    "$PROJECT_SRC/" "$TARGET_WS/"

echo "==> Sourcing ROS2..."
source /opt/ros/humble/setup.bash

echo "==> Building with colcon..."
cd "$TARGET_WS"
colcon build --symlink-install

echo ""
echo "==> Build complete."
echo ""
echo "Next steps (run in TWO separate terminals):"
echo ""
echo "Terminal 1 - launch infrastructure:"
echo "  source /opt/ros/humble/setup.bash"
echo "  source $TARGET_WS/install/setup.bash"
echo "  ros2 launch homebot homebot.launch.py"
echo ""
echo "Terminal 2 - interactive dispatcher:"
echo "  source /opt/ros/humble/setup.bash"
echo "  source $TARGET_WS/install/setup.bash"
echo "  ros2 run homebot task_dispatcher"
echo ""
echo "Run unit tests (no ROS2 needed):"
echo "  cd $TARGET_WS && pytest src/homebot/test/ -v"
