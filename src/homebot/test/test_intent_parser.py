"""
Unit tests for the intent parser.

These tests do NOT import rclpy or require any ROS2 environment.
Run from the package root with:
  pytest test/ -v

Or from the workspace root with:
  pytest src/homebot/test/ -v
"""

import os
import sys

# Allow `from homebot.intent_parser import ...` without installing.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from homebot.intent_parser import parse_intent, extract_room


class TestExtractRoom:

    def test_kitchen(self):
        assert extract_room("inspect the kitchen") == "kitchen"

    def test_living_room_with_space(self):
        assert extract_room("go to the living room") == "living_room"

    def test_living_room_alias_lounge(self):
        assert extract_room("check the lounge") == "living_room"

    def test_charging_station_alias_dock(self):
        assert extract_room("head to dock") == "charging_station"

    def test_unknown_room(self):
        assert extract_room("go somewhere") == "unknown"


class TestParseIntent:

    def test_navigate_kitchen(self):
        r = parse_intent("Inspect the kitchen")
        assert r['action'] == 'navigate'
        assert r['room'] == 'kitchen'

    def test_navigate_bedroom(self):
        r = parse_intent("Go to bedroom")
        assert r['action'] == 'navigate'
        assert r['room'] == 'bedroom'

    def test_sensor_query_temperature(self):
        r = parse_intent("Check living room temperature")
        assert r['action'] == 'sensor_query'
        assert r['room'] == 'living_room'

    def test_sensor_query_humidity(self):
        r = parse_intent("What is the humidity in the kitchen?")
        assert r['action'] == 'sensor_query'
        assert r['room'] == 'kitchen'

    def test_charge_explicit(self):
        r = parse_intent("Go to charging station")
        assert r['action'] == 'charge'
        assert r['room'] == 'charging_station'

    def test_charge_alias_recharge(self):
        r = parse_intent("recharge please")
        assert r['action'] == 'charge'

    def test_charge_has_priority_over_navigate(self):
        # "go to charging station" matches both navigate and charge
        # patterns; charge wins because it is checked first.
        r = parse_intent("go to charging station")
        assert r['action'] == 'charge'

    def test_unknown_intent(self):
        r = parse_intent("play some music")
        assert r['action'] == 'unknown'

    def test_empty_string(self):
        r = parse_intent("")
        assert r['action'] == 'unknown'

    def test_case_insensitive(self):
        r = parse_intent("INSPECT THE KITCHEN")
        assert r['action'] == 'navigate'
        assert r['room'] == 'kitchen'
