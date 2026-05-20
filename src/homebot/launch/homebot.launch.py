"""
homebot.launch.py
-----------------
Starts the infrastructure nodes (sensor_node + robot_simulator)
with a single command:
  ros2 launch homebot homebot.launch.py

The task_dispatcher is intentionally NOT included here because
it is interactive (reads stdin). Run it in a separate terminal:
  ros2 run homebot task_dispatcher
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import LogInfo, TimerAction
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:

    config_file = os.path.join(
        get_package_share_directory('homebot'),
        'config',
        'params.yaml',
    )

    sensor_node = Node(
        package='homebot',
        executable='sensor_node',
        name='sensor_node',
        output='screen',
        parameters=[config_file],
    )

    robot_simulator = Node(
        package='homebot',
        executable='robot_simulator',
        name='robot_simulator',
        output='screen',
        parameters=[config_file],
    )

    ready_msg = TimerAction(
        period=1.0,
        actions=[LogInfo(msg=(
            '\n'
            '  +-----------------------------------------+\n'
            '  |  HomeBot is running.                    |\n'
            '  |  In a new terminal, run:                |\n'
            '  |    ros2 run homebot task_dispatcher     |\n'
            '  +-----------------------------------------+'
        ))]
    )

    return LaunchDescription([
        sensor_node,
        robot_simulator,
        ready_msg,
    ])
