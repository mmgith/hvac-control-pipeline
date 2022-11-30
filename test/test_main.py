import unittest
import sys
import logging
import requests
import json
import time
import os
import mysql.connector as mysql
from signalrcore.hub_connection_builder import HubConnectionBuilder
from src.main import Main

HOST = os.environ["HVAC_HOST"]
TOKEN = os.environ["HVAC_TOKEN"]
TICKETS = os.environ["HVAC_TICKETS"]


class TestStringMethods(unittest.TestCase):
    def test_simulator_up(self):
        r = requests.get(f"{HOST}/api/health")
        self.assertEqual("All system operational Commander !", r.text)

    def test_turn_off_unit(self):
        r = requests.get(f"{HOST}/api/HVAC/{TOKEN}/TurnOffHvac")
        res_payload_dict = r.json()
        self.assertEqual("Turning off Hvac", res_payload_dict["Response"])

    def test_turn_on_AC(self):
        r = requests.get(f"{HOST}/api/HVAC/{TOKEN}/TurnOnAc/{TICKETS}")
        res_payload_dict = r.json()
        self.assertEqual(
            f"Activating AC for {TICKETS} ticks", res_payload_dict["Response"]
        )

    def test_turn_on_Heater(self):
        r = requests.get(f"{HOST}/api/HVAC/{TOKEN}/TurnOnHeater/{TICKETS}")
        res_payload_dict = r.json()
        self.assertEqual(
            f"Activating Heater for {TICKETS} ticks", res_payload_dict["Response"]
        )


class TestHVACMethods(unittest.TestCase):
    def test_AC(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{HOST}/SensorHub?token={TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 2,
                }
            )
            .build()
        )
        values = []
        self._hub_connection.on(
            "ReceiveSensorData", lambda data: values.append(data[0]["data"])
        )
        self._hub_connection.on_open(lambda: print("||| Getting initial value."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.start()
        while len(values) < 1:
            pass
        self._hub_connection.stop()
        r = requests.get(f"{HOST}/api/hvac/{TOKEN}/TurnOnAc/{TICKETS}")
        self._hub_connection.on_open(
            lambda: print("||| Getting values after AC activation.")
        )
        self._hub_connection.start()
        while len(values) < int(TICKETS) - 1:
            pass
        self._hub_connection.stop()
        for i in range(len(values) - 1):
            self.assertGreater(float(values[i]), float(values[i + 1]))

    def test_Heater(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{HOST}/SensorHub?token={TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 2,
                }
            )
            .build()
        )
        values = []
        self._hub_connection.on(
            "ReceiveSensorData", lambda data: values.append(data[0]["data"])
        )
        self._hub_connection.on_open(lambda: print("||| Getting initial value."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.start()
        while len(values) < 1:
            pass
        self._hub_connection.stop()
        r = requests.get(f"{HOST}/api/hvac/{TOKEN}/TurnOnHeater/{TICKETS}")
        self._hub_connection.on_open(
            lambda: print("||| Getting values after Heather activation.")
        )
        self._hub_connection.start()
        while len(values) < int(TICKETS) - 1:
            pass
        self._hub_connection.stop()
        for i in range(len(values) - 1):
            self.assertLess(float(values[i]), float(values[i + 1]))


if __name__ == "__main__":
    unittest.main()
