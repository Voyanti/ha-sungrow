from time import sleep
import atexit
import logging

from modbus_mqtt import MqttClient
from loader import ConfigLoader
# from client import ModbusRtuClient as Client
from server import Server
from sungrow_inverter import SungrowInverter

from client import SpoofClient as Client

logging.basicConfig(
    level=logging.INFO,  # Set logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format with timestamp
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)
logger = logging.getLogger(__name__)

mqtt_client = None


def exit_handler(servers, modbus_clients, mqtt_client):             # TODO check argument passing
    logger.info("Exiting")
    # publish offline availability for each server
    # for server in servers:
        # mqtt_client.publish(f"{}")                  #
    logger.info("Closing client connections on exit")
    for client in modbus_clients:
        client.close()

    mqtt_client.loop_stop()

atexit.register(exit_handler, mqtt_client)

try:
    # Read configuration
    servers_cfgs, clients_cfgs, connection_specs, mqtt_cfg = ConfigLoader.load()
    # Instantiate clients (modbus adapters)
    clients = [Client.from_config(client_cfg, connection_specs) for client_cfg in clients_cfgs]
    # Instantiate servers
    servers = [SungrowInverter.from_config(server_cfg, clients) for server_cfg in servers_cfgs]


    # Connect to clients
    for client in clients:
        client.connect()

    # Connect to Servers
    # for server in Servers:
        # server.verify_serialnum()                              
            
        # server.read_model()
        # modelcode = server.connected_client.read_register(server, "Device Type Code", server.registers["Device Type Code"])
        # sever.model = Server.device_info[modelcode]
        # TODO find valid registers
        # - get limits for settable params TODO

    # Setup MQTT Client
    mqtt_client = MqttClient(mqtt_cfg)
    mqtt_client.connect(host=mqtt_cfg["host"], port=mqtt_cfg["port"])
    mqtt_client.loop_start()
    
    # Publish Discovery Topics
    for server in servers:
        mqtt_client.publish_discovery_topics()

    # every read_interval seconds, read the registers and publish to mqtt
    while True:
        for server in servers:
            for register, details in server.registers.items():
                client = server.connected_client
                value = client.read_register(server, register, details)
                mqtt_client.publish(register, value)

        # publish availability

        sleep(config.read_interval)
finally:
    exit_handler(servers, clients, mqtt_client)
