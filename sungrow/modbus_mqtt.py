import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
import logging

from random import getrandbits
from time import time
logger = logging.getLogger(__name__)

class MqttClient(mqtt.Client):
    def __init__(self, mqtt_cfg):
        def generate_uuid():
            random_part = getrandbits(64)
            timestamp = int(time() * 1000)  # Get current timestamp in milliseconds
            node = getrandbits(48)  # Simulating a network node (MAC address)

            uuid_str = f'{timestamp:08x}-{random_part >> 32:04x}-{random_part & 0xFFFF:04x}-{node >> 24:04x}-{node & 0xFFFFFF:06x}'
            return uuid_str
            
        uuid = generate_uuid()
        super().__init__(CallbackAPIVersion.VERSION2, f"modbus-{uuid}")
        self.username_pw_set(mqtt_cfg["user"], mqtt_cfg["password"])
        self.mqtt_cfg = mqtt_cfg

    def on_connect(self, userdata, flags, rc):
        logger.info("Connected to MQTT broker")
        # subscribe to set topics (get from server implementation)

    def on_disconnect(self, userdata, rc):
        logger.info("Disconnected from MQTT broker")
        pass

    def on_message(self, userdata, rc):
        pass

    def publish_discovery_topics(self, server):
        # from uxr_charger app
        # server.model = "test"
        # server.serialnum = "asdf1234"

        device = {
            "manufacturer": server.manufacturer,
            "model": server.model,
            "identifiers": [f"{server.manufacturer}_{server.serialnum}"],
            "name": f"{server.manufacturer} {server.serialnum}"
        }

        # publish discovery topics for legal registers
        # assume registers in server.registers

        # from uxr_charger app
        for register_name, details in server.valid_read_registers:
            discovery_payload = {
                    "name": register_name,
                    "unique_id": f"uxr_{server.serialnum}_{register_name.replace(' ', '_').lower()}",
                    "state_topic": f"{mqtt_cfg['base_topic']}/{server.serialnum}/{register_name.replace(' ', '_').lower()}",
                    "availability_topic": availability_topic,
                    "device": device,
                    "device_class": details.get("device_class"),        # TODO add
                    "unit_of_measurement": details.get("unit"),
                }
            discovery_topic = f"{mqtt_cfg['ha_discovery_topic']}/sensor/{server.manufacturer.lower()}_{server.serialnum}/{registername.replace(' ', '_').lower()}/config"
            server.connected_client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)

        # TODO incomplete