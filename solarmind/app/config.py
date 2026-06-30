from dataclasses import dataclass
import json
import os


@dataclass
class Config:
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str


def load_config() -> Config:
    defaults = {
        "mqtt_host": "core-mosquitto",
        "mqtt_port": 1883,
        "mqtt_username": "ha-mqtt",
        "mqtt_password": "9jjiVawEV5ZjvV8",
    }

    path = "/data/options.json"

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            options = json.load(f)
        defaults.update(options)

    return Config(**defaults)