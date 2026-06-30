import json
import os
import time
import traceback
import paho.mqtt.client as mqtt

VERSION = "1.0.0-beta"


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

    log(f"STEP 1 OK - Options loaded")
    return options


def publish_sensor(client, object_id, name, state, icon=None, unit=None, attributes=None):
    base_topic = f"solarmind/{object_id}"
    discovery_topic = f"homeassistant/sensor/solarmind/{object_id}/config"
    state_topic = f"{base_topic}/state"
    attributes_topic = f"{base_topic}/attributes"
    availability_topic = "solarmind/status/availability"

    payload = {
        "name": name,
        "object_id": f"solarmind_{object_id}",
        "unique_id": f"solarmind_{object_id}",
        "state_topic": state_topic,
        "json_attributes_topic": attributes_topic,
        "availability_topic": availability_topic,
        "payload_available": "online",
        "payload_not_available": "offline",
        "device": {
            "identifiers": ["solarmind"],
            "name": "SolarMind",
            "manufacturer": "SolarMind",
            "model": "Home Assistant Add-on",
            "sw_version": VERSION,
        },
    }

    if icon:
        payload["icon"] = icon

    if unit:
        payload["unit_of_measurement"] = unit

    client.publish(discovery_topic, json.dumps(payload), retain=True)
    client.publish(state_topic, str(state), retain=True)
    client.publish(attributes_topic, json.dumps(attributes or {}), retain=True)


def publish_bootstrap_sensors(client):
    errors = []
    health = 100 if not errors else 50

    publish_sensor(
        client,
        "status",
        "Status",
        "online",
        icon="mdi:solar-power-variant",
        attributes={
            "version": VERSION,
            "source": "SolarMind",
        },
    )

    publish_sensor(
        client,
        "system_health",
        "System Health",
        health,
        icon="mdi:heart-pulse",
        unit="%",
        attributes={
            "version": VERSION,
            "errors": errors,
        },
    )

    publish_sensor(
        client,
        "system_errors",
        "System Errors",
        len(errors),
        icon="mdi:alert-circle-outline",
        attributes={
            "version": VERSION,
            "errors": errors,
        },
    )


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

        client.publish("solarmind/status/availability", "online", retain=True)

        publish_bootstrap_sensors(client)
        log("PUBLISH - Bootstrap sensors published")

        log("READY - SolarMind add-on started")

        while True:
            publish_bootstrap_sensors(client)
            log("PUBLISH - Bootstrap sensors published")
            time.sleep(60)

    except Exception as error:
        log(f"FATAL - {error}")
        traceback.print_exc()
        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()