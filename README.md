# homebot_dispatcher

A minimal Language-to-Robot proof of concept using ROS2 Humble.

A user types a natural language command. A dispatcher node parses
the intent and publishes a structured task to a ROS2 topic. A
simulated robot node subscribes, executes the task, and reports
status back. A sensor node streams fake IoT readings independently.

Built to explore ROS2 communication patterns — not to impress,
but to understand.

---

## Architecture

```
    [CLI input]
        |  raw text
        v
    [task_dispatcher node]
        |  /robot/task  (std_msgs/String, JSON)
        v
    [robot_simulator node] ---> /robot/status  (std_msgs/String, JSON)

    [sensor_node] ------------> /home/sensors/{room}  (1 Hz, independent)

    [/get_robot_position service]  (std_srvs/Trigger, synchronous)
```

## ROS2 Concepts Demonstrated

| Concept            | Where used                                     | Why                                           |
| ------------------ | ---------------------------------------------- | --------------------------------------------- |
| Topics (pub/sub)   | `/robot/task`, `/robot/status`, `/home/sensors/*` | Async, decoupled communication             |
| Services           | `/get_robot_position`                          | Synchronous query needing a guaranteed reply  |
| Parameters         | `config/params.yaml`                           | Runtime config without hardcoding             |
| Launch files       | `launch/homebot.launch.py`                     | Start all nodes with one command              |
| Threading in nodes | `robot_simulator.py`                           | Never block the ROS2 executor in a callback   |

## Requirements

- Ubuntu 22.04 (WSL2 is fine)
- ROS2 Humble
- Python 3.10+

## Quick Start

```bash
# Terminal 1 - launch infrastructure
source /opt/ros/humble/setup.bash
cd ~/homebot_ws && source install/setup.bash
ros2 launch homebot homebot.launch.py

# Terminal 2 - interactive dispatcher
source /opt/ros/humble/setup.bash
cd ~/homebot_ws && source install/setup.bash
ros2 run homebot task_dispatcher
```

## Example Commands

| Input                              | Action       | Room             |
| ---------------------------------- | ------------ | ---------------- |
| `inspect the kitchen`              | navigate     | kitchen          |
| `check living room temperature`    | sensor_query | living_room      |
| `go to charging station`           | charge       | charging_station |
| `patrol the hallway`               | navigate     | hallway          |

## Tests

```bash
cd ~/homebot_ws
pytest src/homebot/test/ -v
```

The intent parser has no ROS2 imports, so the tests run without
sourcing any ROS2 environment. That separation is intentional.

## Limitations (honest notes)

- Intent parsing is rule-based regex; it is not robust to
  arbitrary phrasing.
- Robot motion is `time.sleep()`, not physics simulation.
- No coordinate system, no real map, no Nav2 integration.
- Sensor readings are randomly generated around per-room baselines.
- Task payloads use JSON-in-String rather than a custom `.msg` type
  (deliberate PoC scope choice).

## What I would add next

1. Replace the rule-based parser with a local LLM via Ollama
   (one function change in `intent_parser.py`, architecture unchanged).
2. Add a ROS2 action server for navigate tasks with real progress
   feedback (percentage complete, ETA).
3. Namespace topics for multi-robot support: `/robot_a/task`, etc.
4. Bridge `/home/sensors/*` to an MQTT broker so real IoT devices
   can publish into the system.
