import json
import os
import time
import paho.mqtt.client as mqtt

VERSION = "0.2.0"


def load_options():
    path = "/data/options.json"
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def publish_status(client):
    discovery_topic = "homeassistant/sensor/solarmind/status/config"
    state_topic = "solarmind/status/state"
    availability_topic = "solarmind/status/availability"

    discovery_payload = {
        "name": "Status",
        "object_id": "solarmind_status",
        "unique_id": "solarmind_status",
        "state_topic": state_topic,
        "availability_topic": availability_topic,
        "payload_available": "online",
        "payload_not_available": "offline",
        "icon": "mdi:solar-power-variant",
        "device": {
            "identifiers": ["solarmind"],
            "name": "SolarMind",
            "manufacturer": "SolarMind",
            "model": "Home Assistant Add-on",
            "sw_version": VERSION,
        },
    }

    client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
    client.publish(availability_topic, "online", retain=True)
    client.publish(state_topic, "online", retain=True)


def main():
    options = load_options()

    mqtt_host = options.get("mqtt_host", "core-mosquitto")
    mqtt_port = int(options.get("mqtt_port", 1883))
    mqtt_username = options.get("mqtt_username", "")
    mqtt_password = options.get("mqtt_password", "")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="solarmind_addon")

    if mqtt_username:
        client.username_pw_set(mqtt_username, mqtt_password)

    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

    publish_status(client)

    print("SolarMind add-on started")
    print("SolarMind status published")

    while True:
        publish_status(client)
        time.sleep(60)


if __name__ == "__main__":
    main()
