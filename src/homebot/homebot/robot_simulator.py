"""
robot_simulator.py
------------------
Simulates a mobile robot that responds to task commands.

Subscriptions:
  /robot/task    (std_msgs/String, JSON)

Publications:
  /robot/status  (std_msgs/String, JSON)

Services:
  /get_robot_position  (std_srvs/Trigger) - returns current room

Task execution runs in a background thread so the ROS2 executor
is never blocked by time.sleep() inside a callback.
"""

import json
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class RobotSimulator(Node):

    def __init__(self):
        super().__init__('robot_simulator')

        self.declare_parameter('current_room', 'charging_station')
        self.declare_parameter('move_duration_sec', 1.5)

        self._current_room = self.get_parameter('current_room').value
        self._move_duration = self.get_parameter('move_duration_sec').value

        # Protects _current_room across executor + worker threads.
        self._room_lock = threading.Lock()

        self.task_sub = self.create_subscription(
            String, '/robot/task', self._on_task_received, 10
        )
        self.status_pub = self.create_publisher(String, '/robot/status', 10)
        self.position_srv = self.create_service(
            Trigger, '/get_robot_position', self._handle_position_request
        )

        self.get_logger().info(
            f'RobotSimulator ready | starting room: {self._current_room}'
        )

    def _on_task_received(self, msg: String) -> None:
        try:
            task = json.loads(msg.data)
        except json.JSONDecodeError as e:
            self.get_logger().error(f'Malformed task message: {e}')
            return

        self.get_logger().info(
            f'Task received - action={task.get("action")} '
            f'room={task.get("room")}'
        )

        # Hand off to a worker so the subscriber callback returns immediately.
        threading.Thread(
            target=self._execute_task, args=(task,), daemon=True
        ).start()

    def _execute_task(self, task: dict) -> None:
        action = task.get('action', 'unknown')
        room   = task.get('room', 'unknown')

        self._publish_status('executing', action, room)

        if action == 'navigate':
            self._simulate_move(room)
            result = f'Arrived at {room.replace("_", " ")}'

        elif action == 'sensor_query':
            self._simulate_move(room)
            result = (
                f'Sensor check at {room.replace("_", " ")} complete. '
                f'See /home/sensors/{room} for live readings.'
            )

        elif action == 'charge':
            self._simulate_move('charging_station')
            result = 'Docked at charging station'

        else:
            result = f'Unknown action "{action}" - no operation performed'
            self.get_logger().warn(result)

        self._publish_status('completed', action, room, result)
        self.get_logger().info(f'Task complete: {result}')

    def _simulate_move(self, destination: str) -> None:
        time.sleep(self._move_duration)
        with self._room_lock:
            self._current_room = destination

    def _publish_status(
        self, state: str, action: str, room: str, detail: str = ''
    ) -> None:
        with self._room_lock:
            current = self._current_room

        payload = {
            'state':        state,
            'action':       action,
            'target_room':  room,
            'current_room': current,
            'detail':       detail,
        }
        msg = String()
        msg.data = json.dumps(payload)
        self.status_pub.publish(msg)

    def _handle_position_request(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        with self._room_lock:
            room = self._current_room
        response.success = True
        response.message = room
        self.get_logger().info(f'Position query -> {room}')
        return response


def main(args=None) -> None:
    rclpy.init(args=args)
    node = RobotSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
