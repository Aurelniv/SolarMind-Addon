import json
import os
import time
import traceback
import paho.mqtt.client as mqtt

VERSION = "0.2.1"


def log(message):
    print(f"[SolarMind] {message}", flush=True)


def load_options():
    log("STEP 1 - Loading add-on options")

    path = "/data/options.json"

    if not os.path.exists(path):
        log("WARNING - /data/options.json not found, using defaults")
        return {}

    with open(path, "r", encoding="utf-8") as file:
        options = json.load(file)

    log(f"STEP 1 OK - Options loaded: {options}")
    return options


def publish_status(client):
    log("STEP 5 - Publishing MQTT discovery and state")

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

    result_discovery = client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
    result_availability = client.publish(availability_topic, "online", retain=True)
    result_state = client.publish(state_topic, "online", retain=True)

    log(f"MQTT publish discovery rc={result_discovery.rc}")
    log(f"MQTT publish availability rc={result_availability.rc}")
    log(f"MQTT publish state rc={result_state.rc}")
    log("STEP 5 OK - MQTT messages published")


def main():
    try:
        log("BOOT - SolarMind add-on starting")
        log(f"VERSION - {VERSION}")

        options = load_options()

        mqtt_host = options.get("mqtt_host", "core-mosquitto")
        mqtt_port = int(options.get("mqtt_port", 1883))
        mqtt_username = options.get("mqtt_username", "")
        mqtt_password = options.get("mqtt_password", "")

        log(f"STEP 2 - MQTT host={mqtt_host} port={mqtt_port}")

        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="solarmind_addon",
        )

        log("STEP 3 OK - MQTT client created")

        if mqtt_username:
            client.username_pw_set(mqtt_username, mqtt_password)
            log("STEP 3B OK - MQTT credentials configured")
        else:
            log("STEP 3B - No MQTT username configured")

        log("STEP 4 - Connecting to MQTT broker")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        log("STEP 4 OK - MQTT connected")

        publish_status(client)

        log("READY - SolarMind add-on started")

        while True:
            publish_status(client)
            time.sleep(60)

    except Exception as error:
        log(f"FATAL - {error}")
        traceback.print_exc()
        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()