"""
intent_parser.py
----------------
Pure Python intent resolver. No ROS2 dependencies.
Maps natural language strings to structured task dictionaries.

Design note: keeping this separate from the ROS2 node means:
  - It can be tested without a running ROS2 environment
  - The parsing logic can be swapped (e.g. for an LLM) without
    touching the node code
  - The boundary between "language" and "robotics" is explicit
"""

import re


ROOM_ALIASES: dict = {
    "kitchen":          "kitchen",
    "living room":      "living_room",
    "livingroom":       "living_room",
    "lounge":           "living_room",
    "bedroom":          "bedroom",
    "hallway":          "hallway",
    "corridor":         "hallway",
    "charging station": "charging_station",
    "charger":          "charging_station",
    "dock":             "charging_station",
    "base":             "charging_station",
}

KNOWN_ROOMS: list = [
    "kitchen",
    "living_room",
    "bedroom",
    "hallway",
    "charging_station",
]


def extract_room(text: str) -> str:
    """
    Find the first room mention in text.
    Returns the canonical room name, or 'unknown' if none found.
    Longer aliases are checked first to avoid partial matches.
    """
    sorted_aliases = sorted(ROOM_ALIASES.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if alias in text:
            return ROOM_ALIASES[alias]
    return "unknown"


def parse_intent(text: str) -> dict:
    """
    Resolve a natural language command to a structured task.

    Returns a dict with at minimum:
      {
        "action": str,   # "navigate" | "sensor_query" | "charge" | "unknown"
        "room":   str,   # canonical room name or "unknown"
      }
    """
    if not text or not text.strip():
        return {"action": "unknown", "room": "unknown", "raw": text}

    t = text.lower().strip()

    # Charging intent is checked first because "go to charging station"
    # would otherwise match the navigate pattern.
    if re.search(r'\b(charge|charging|dock|recharge|go home|return home)\b', t):
        return {"action": "charge", "room": "charging_station"}

    if re.search(r'\b(temperature|temp|hot|cold|warm|humid|humidity|sensor)\b', t):
        return {"action": "sensor_query", "room": extract_room(t)}

    if re.search(
        r'\b(inspect|check|go to|navigate|move to|patrol|scan|visit|head to)\b', t
    ):
        return {"action": "navigate", "room": extract_room(t)}

    return {"action": "unknown", "room": "unknown", "raw": text}
