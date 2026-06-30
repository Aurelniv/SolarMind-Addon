import json
import os
import time
import paho.mqtt.client as mqtt


VERSION = "0.1.0"


def load_addon_options():
    options_path = "/data/options.json"
    if not os.path.exists(options_path):
        return {}

    with open(options_path, "r", encoding="utf-8") as file:
        return json.load(file)


def publish_status():
    options = load_addon_options()

    mqtt_host = options.get("mqtt_host", "core-mosquitto")
    mqtt_port = int(options.get("mqtt_port", 1883))
    mqtt_username = options.get("mqtt_username", "")
    mqtt_password = options.get("mqtt_password", "")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="solarmind_addon")

    if mqtt_username:
        client.username_pw_set(mqtt_username, mqtt_password)

    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

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

    print("SolarMind status published")


def main():
    publish_status()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
