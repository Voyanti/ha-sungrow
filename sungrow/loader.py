import json
import os
import logging
logger = logging.getLogger(__name__)


class ConfigLoader:
   
    @staticmethod
    def load(json_rel_path="data/options.json") -> tuple[dict, dict]:
        """ Load server, client configurations and connection specs as dicts from options json. """

        logger.info("Attempting to read configuration json")
        if os.path.exists(json_rel_path):
            with open(json_rel_path) as f:
                data = json.load(f)
        else:
            raise FileNotFoundError(f"Config options json not found.")

        cls.validate(data)
        logger.info("Successfully read configuration json")

        return data["servers"], data["clients"], data["connection_specs"], data["mqtt"]

    @staticmethod
    def validate(data):
        pass

# Option schema example
# {'clients': [{'name': 'usb_to_modbus',
#     'nickname': 'Client1',
#     'connection_specs': 'SunGrow Inverter',
#     'port': 'dev/tty1'}],
#   'servers': [{'name': 'SunGrow Inverter 1',
#     'nickname': 'SG1',
#     'serialnum': '12345678',
#     'server_type': 'SunGrow Inverter',
#     'connected_client': 'Client1'}],
#   'connection_specs': {'SunGrow Inverter': {'connection_method': 'RTU',
#     'baudrate': 9600,
#     'bytesize': 8,
#     'parity': False,
#     'stopbits': 1}}}
