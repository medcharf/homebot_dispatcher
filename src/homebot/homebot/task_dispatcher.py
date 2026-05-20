"""
task_dispatcher.py
------------------
Entry point for user commands. Reads natural language input,
resolves intent, and publishes structured tasks to /robot/task.

Also subscribes to /robot/status to echo feedback to the user.

rclpy.spin() runs in a background thread so the main thread can
block on input() without freezing the node.
"""

import json
import sys
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from homebot.intent_parser import parse_intent


class TaskDispatcher(Node):

    def __init__(self):
        super().__init__('task_dispatcher')

        self.task_pub = self.create_publisher(String, '/robot/task', 10)
        self.status_sub = self.create_subscription(
            String, '/robot/status', self._on_status, 10
        )

        self.get_logger().info('TaskDispatcher ready')

    def dispatch(self, raw_text: str) -> bool:
        intent = parse_intent(raw_text)

        if intent['action'] == 'unknown':
            self.get_logger().warn(
                f'Could not parse: "{raw_text}" - '
                'try: inspect/check/go to/temperature + room name'
            )
            return False

        msg = String()
        msg.data = json.dumps(intent)
        self.task_pub.publish(msg)

        self.get_logger().info(
            f'Dispatched -> action={intent["action"]} room={intent["room"]}'
        )
        return True

    def _on_status(self, msg: String) -> None:
        try:
            s = json.loads(msg.data)
        except json.JSONDecodeError:
            return

        state  = s.get('state', '?').upper()
        detail = s.get('detail', '')
        room   = s.get('current_room', '?')

        if detail:
            print(f'\n  [{state}] {detail} (now at: {room})')
        else:
            print(f'\n  [{state}] Robot is at: {room}')

        print('> ', end='', flush=True)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TaskDispatcher()

    # spin() and input() both block; they cannot share the main thread.
    spin_thread = threading.Thread(
        target=rclpy.spin, args=(node,), daemon=True
    )
    spin_thread.start()

    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        print(f'One-shot: "{command}"')
        node.dispatch(command)
        spin_thread.join(timeout=4.0)
        node.destroy_node()
        rclpy.shutdown()
        return

    print('-' * 50)
    print('  HomeBot Dispatcher - interactive mode')
    print('  Examples:')
    print('    > inspect the kitchen')
    print('    > check living room temperature')
    print('    > go to charging station')
    print('  Ctrl+C to quit')
    print('-' * 50)

    try:
        while rclpy.ok():
            try:
                raw = input('> ')
            except EOFError:
                break
            if raw.strip():
                node.dispatch(raw)
    except KeyboardInterrupt:
        pass
    finally:
        print('\nShutting down dispatcher...')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
