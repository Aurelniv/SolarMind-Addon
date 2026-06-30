import json
import os
import time
import traceback

import paho.mqtt.client as mqtt
import requests

from config import load_config


VERSION = "1.0.1-beta"
HA_TEST_ENTITY = "sensor.sun_solar_azimuth"


def log(message):
    print(f"[SolarMind] {message}", flush=True)


def load_options():
    path = "/data/options.json"

    if not os.path.exists(path):
        log("WARNING - /data/options.json not found, using defaults")
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_ha_token():
    return os.environ.get("SUPERVISOR_TOKEN", "")


def read_ha_state(entity_id):
    token = get_ha_token()

    if not token:
        raise RuntimeError("SUPERVISOR_TOKEN unavailable")

    url = f"http://supervisor/core/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    return response.json()


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


def publish_bootstrap_sensors(client, errors):
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


def publish_ha_test_value(client):
    ha_data = read_ha_state(HA_TEST_ENTITY)

    value = ha_data.get("state", "unknown")

    publish_sensor(
        client,
        "ha_test_value",
        "HA Test Value",
        value,
        icon="mdi:home-assistant",
        attributes={
            "version": VERSION,
            "source_entity": HA_TEST_ENTITY,
            "ha_attributes": ha_data.get("attributes", {}),
        },
    )

    log(f"HA API - {HA_TEST_ENTITY}={value}")


def main():
    try:
        log("BOOT - SolarMind add-on starting")
        log(f"VERSION - {VERSION}")

        config = load_config()

        mqtt_host = config.mqtt_host
        mqtt_port = config.mqtt_port
        mqtt_username = config.mqtt_username
        mqtt_password = config.mqtt_password

        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="solarmind_addon",
        )

        if mqtt_username:
            client.username_pw_set(mqtt_username, mqtt_password)

        log(f"MQTT - Connecting to {mqtt_host}:{mqtt_port}")
        client.connect(mqtt_host, mqtt_port, 60)
        client.loop_start()
        client.publish("solarmind/status/availability", "online", retain=True)

        log("MQTT - Connected")
        log("READY - SolarMind add-on started")

        while True:
            errors = []

            try:
                publish_ha_test_value(client)
            except Exception as error:
                errors.append(f"HA API test failed: {error}")
                log(f"ERROR - HA API test failed: {error}")

            publish_bootstrap_sensors(client, errors)
            log("PUBLISH - Bootstrap sensors published")

            time.sleep(60)

    except Exception as error:
        log(f"FATAL - {error}")
        traceback.print_exc()

        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()