from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.constants import Endian
import struct
import logging
logger = logging.getLogger(__name__)

from server import Server

DEBUG = True
def debug(content):
    if DEBUG: print(content)

class ModbusRtuClient:
    def __init__(self, name:str, nickname:str, port:int, baudrate:int, bytesize:int=8, parity:bool=False, stopbits:int=1, timeout:int=1):
        self.name = name
        self.nickname = nickname
        self.client = ModbusSerialClient(   port=port, baudrate=baudrate, 
                                            bytesize=bytesize, parity=parity, stopbits=stopbits, 
                                            timeout=timeout)


    def read_registers(self, server:Server, register_name:str, register_info:dict):
        """ Read a group of registers using pymodbus 
        
            Reuires implementation of the abstract method 'Server._decoded()'
        """

        address = register_info["addr"]
        dtype =  register_info["dtype"]
        multiplier = register_info["multiplier"]
        unit = register_info["unit"]
        count = register_info["count"]

        result = self.client.read_holding_registers(address-1,
                                                    count=count,
                                                    slave=server.device_addr)

        if result.isError():
            raise Exception(f"Error reading register {register_name}")

        return server._decoded(result.registers, dtype)
        return _decoded(result.registers)*multiplier
        # TODO multiplier

    def write_register(self, val, is_float:bool, server:Server, register_name: str, register_info:dict):
        """ Write to an individual register using pymodbus.

            Reuires implementation of the abstract methods 
            'Server._validate_write_val()' and 'Server._encode()'
        """
        # model specific write register validation
        server._validate_write_val(register_name, val)
        
        self.client.write_register(address=register_info["addr"],
                                    value=server._encoded(value),
                                    slave=server.device_addr)


    def connect(self):
        self.client.connect()

    def close(self):
        self.client.close()

    def from_config(client_cfg: dict, connection_cfg: dict):
        try:
            idx = [c['name'] for c in connection_cfg].index(client_cfg["connection_specs"])  # TODO ugly
        except:
            raise ValueError(f"Connection config {client_cfg['connection_specs']} for client {client_cfg['nickname']} not defined in options.")

        return ModbusRtuClient(client_cfg["name"], client_cfg["nickname"], client_cfg["port"], 
                            connection_cfg[idx]["baudrate"], connection_cfg[idx]["bytesize"], 
                            connection_cfg[idx]["parity"], connection_cfg[idx]["stopbits"])

    def __str__(self):
        return f"{self.nickname}"

class SpoofClient(ModbusRtuClient):
    def read_registers(self, server:Server, register_name:str, register_info:dict):
        """ Read a group of registers using pymodbus 
        
            Reuires implementation of the abstract method 'Server._decoded()'
        """

        address = register_info["addr"]
        dtype =  register_info["dtype"]
        multiplier = register_info["multiplier"]
        unit = register_info["unit"]
        count = register_info["count"]

        # result = self.client.read_holding_registers(address-1,
                                                    # count=count,
                                                    # slave=server.device_addr)

        # if result.isError():
        #     raise Exception(f"Error reading register {register_name}")

        return server._decoded([258,], dtype="U16")
        # return _decoded(result.registers)*multiplier
        # TODO multiplier

    def write_register(self, val, is_float:bool, server:Server, register_name: str, register_info:dict):
        """ Write to an individual register using pymodbus.

            Reuires implementation of the abstract methods 
            'Server._validate_write_val()' and 'Server._encode()'
        """
        # model specific write register validation
        server._validate_write_val(register_name, val)
        
        # self.client.write_register(address=register_info["addr"],
        #                             value=server._encoded(value),
        #                             slave=server.device_addr)
        return None

    def connect(self):
        logger.info("Connect spoof")

    def close(self):
        logger.info("Disconnect spoof")


