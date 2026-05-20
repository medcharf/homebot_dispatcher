"""
sensor_node.py
--------------
Simulates IoT sensors in each room.
Publishes fake temperature + humidity readings at a fixed rate.

Topics published:
  /home/sensors/kitchen       (std_msgs/String, JSON)
  /home/sensors/living_room   (std_msgs/String, JSON)
  /home/sensors/bedroom       (std_msgs/String, JSON)
  /home/sensors/hallway       (std_msgs/String, JSON)

This node runs independently of the robot.
"""

import json
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


ROOMS = ["kitchen", "living_room", "bedroom", "hallway"]

ROOM_BASELINES = {
    "kitchen":     22.0,
    "living_room": 21.0,
    "bedroom":     19.5,
    "hallway":     18.0,
}


class SensorNode(Node):

    def __init__(self):
        super().__init__('sensor_node')

        self.declare_parameter('publish_rate_hz', 1.0)
        rate = self.get_parameter('publish_rate_hz').value
        period = 1.0 / rate

        self.publishers_ = {
            room: self.create_publisher(String, f'/home/sensors/{room}', 10)
            for room in ROOMS
        }

        self.timer = self.create_timer(period, self.publish_readings)
        self.get_logger().info(
            f'SensorNode started - publishing {len(ROOMS)} rooms at {rate} Hz'
        )

    def publish_readings(self) -> None:
        for room in ROOMS:
            baseline = ROOM_BASELINES.get(room, 20.0)
            payload = {
                "room":          room,
                "temperature_c": round(baseline + random.uniform(-1.5, 1.5), 1),
                "humidity_pct":  round(random.uniform(40.0, 65.0), 1),
                "timestamp_sec": self.get_clock().now().nanoseconds / 1e9,
            }
            msg = String()
            msg.data = json.dumps(payload)
            self.publishers_[room].publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
