import json
import os
import logging
logger = logging.getLogger(__name__)


class ConfigLoader:
   
    @staticmethod
    def load(json_rel_path="/data/options.json") -> tuple[dict, dict]:
        """ Load server, client configurations and connection specs as dicts from options json. """

        logger.info("Attempting to read configuration json")
        if os.path.exists(json_rel_path):
            with open(json_rel_path) as f:
                data = json.load(f)
        elif os.path.exists('data/config.yaml'):
            logging.info("Loading config.yaml")
            with open(r'data/config.yaml') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)['options']
        else:
            raise FileNotFoundError(f"Config options json not found.")

        cls.validate(data)
        logger.info("Successfully read configuration")

        return data["servers"], data["clients"], data["connection_specs"], data["mqtt"]

    @staticmethod
    def validate(data):
        pass
