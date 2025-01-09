from config_loader import ConfigLoader
# from client import ModbusRtuClient as Client
# from Sensor import Sensor

class Server:
    
    def __init__(self, name:str, nickname:str, serialnum:str, connected_client):
        self.name = name
        self.nickname= nickname
        self.serialnum = serialnum
        self.connected_client = connected_client
        self.registers: list = []
        # self.batches TODO

    def batchify_registers(self):
        pass

    def from_config(server_cfg:dict, clients:list):
        # assume valid configLoader object
        try:
            idx = [str(client) for c in clients].index(server_cfg["connected_client"])  # TODO ugly
        except:
            raise ValueError(f"Client {server_cfg['connected_client']} from server {server_cfg['nickname']} config not defined in client list")

        return Server(server_cfg["name"], server_cfg["nickname"], server_cfg["serialnum"], connected_client=clients[idx])



