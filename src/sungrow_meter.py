from typing import Optional, final
from .server import Server
from .client import Client
from .enums import DeviceClass, Parameter, RegisterTypes, DataType
from .loader import ServerOptions, SungrowMeterOptions
from pymodbus.client import ModbusSerialClient
import logging

logger = logging.getLogger(__name__)



@final
class AcrelMeter(Server):
    
    # subset of all registers in documentation
    # regisister definitions in document are 0-indexed. Add 1
    @staticmethod   
    def get_registers(VOLTAGE_MULTIPLIER, CURRENT_MULTIPLIER, POWER_MULTIPLIER, ENERGY_MULTIPLIER, meter_reverse_connection: Optional[bool]) -> dict[str, Parameter]:
        logger.info(f"{VOLTAGE_MULTIPLIER=}; {CURRENT_MULTIPLIER=}; {POWER_MULTIPLIER=}; {ENERGY_MULTIPLIER=};")

        multiplier_apparant_power_and_pf = -1 if meter_reverse_connection is not None and meter_reverse_connection else 1
        relevant_registers: dict[str, Parameter] = {
            "Phase A Voltage": {
                "addr": 0x0061+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "V",
                "device_class": DeviceClass.VOLTAGE,
                "multiplier": VOLTAGE_MULTIPLIER
            },
            "Phase B Voltage": {
                "addr": 0x0062+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "V",
                "device_class": DeviceClass.VOLTAGE,
                "multiplier": VOLTAGE_MULTIPLIER
            },
            "Phase C Voltage": {
                "addr": 0x0063+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "V",
                "device_class": DeviceClass.VOLTAGE,
                "multiplier": VOLTAGE_MULTIPLIER
            },
            "A-B Line Voltage": {
                "addr": 0x0078+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "V",
                "device_class": DeviceClass.VOLTAGE,
                "multiplier": VOLTAGE_MULTIPLIER
            },
            "B-C Line Voltage": {
                "addr": 0x0079+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "V",
                "device_class": DeviceClass.VOLTAGE,
                "multiplier": VOLTAGE_MULTIPLIER
            },
            "C-A Line Voltage": {
                "addr": 0x007A+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "V",
                "device_class": DeviceClass.VOLTAGE,
                "multiplier": VOLTAGE_MULTIPLIER
            },
            "Phase A Current": {
                "addr": 0x0064+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "A",
                "device_class": DeviceClass.CURRENT,
                "multiplier": CURRENT_MULTIPLIER
            },
            "Phase B Current": {
                "addr": 0x0065+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "A",
                "device_class": DeviceClass.CURRENT,
                "multiplier": CURRENT_MULTIPLIER
            },
            "Phase C Current": {
                "addr": 0x0066+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "A",
                "device_class": DeviceClass.CURRENT,
                "multiplier": CURRENT_MULTIPLIER
            },
            "Phase A Active Power": {
                "addr": 0x0164+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kW",
                "device_class": DeviceClass.POWER,
                "state_class": "measurement",
                "multiplier": POWER_MULTIPLIER
            },
            "Phase B Active Power": {
                "addr": 0x0166+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kW",
                "device_class": DeviceClass.POWER,
                "state_class": "measurement",
                "multiplier": POWER_MULTIPLIER
            },
            "Phase C Active Power": {
                "addr": 0x0168+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kW",
                "device_class": DeviceClass.POWER,
                "state_class": "measurement",
                "multiplier": POWER_MULTIPLIER
            },
            "PF": {
                "addr": 0x017F+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I16,
                "unit": "",
                "device_class": DeviceClass.POWER_FACTOR,
                "multiplier": 0.001*multiplier_apparant_power_and_pf # reversed if meter reversed
            },
            "Grid Frequency": {
                "addr": 0x0077+1,
                "count": 1,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.U16,
                "unit": "Hz",
                "device_class": DeviceClass.FREQUENCY,
                "multiplier": 0.01
            },
            "Active Power": {
                "addr": 0x016A+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kW",
                "device_class": DeviceClass.POWER,
                "state_class": "measurement",
                "multiplier": POWER_MULTIPLIER
            },
            "Reactive Power": {
                "addr": 0x0172+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kvar",
                "device_class": DeviceClass.REACTIVE_POWER,
                "state_class": "measurement",
                "multiplier": POWER_MULTIPLIER
            },
            "Apparent Power": {
                "addr": 0x017A+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kVA",
                "device_class": DeviceClass.APPARENT_POWER,
                "state_class": "measurement",
                "multiplier": POWER_MULTIPLIER*multiplier_apparant_power_and_pf # reversed if meter reversed
            },
        }

        forward_energy_params: dict[str, Parameter]  = {
            "Total Grid Import": {                    # was 'Forward Active Energy'
                "addr": 0x000A+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kWh",
                "device_class": DeviceClass.ENERGY,
                "multiplier": ENERGY_MULTIPLIER,
                'state_class': 'total'
            },
            "Total Grid Export": {                    # was 'Reverse Active Energy'
                "addr": 0x0014+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kWh",
                "device_class": DeviceClass.ENERGY,
                "multiplier": ENERGY_MULTIPLIER,
                'state_class': 'total'
            },
            "Forward Reactive Energy": {
                "addr": 0x0028+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kvarh",
                "device_class": DeviceClass.ENERGY,
                "multiplier": ENERGY_MULTIPLIER
            },
            "Reverse Reactive Energy": {
                "addr": 0x0032+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kvarh",
                "device_class": DeviceClass.ENERGY,
                "multiplier": ENERGY_MULTIPLIER
            }
        }

        # When the meter connection is reversed, swop the import and export energy values
        reverse_energy_params: dict[str, Parameter]  = {
            "Total Grid Export": {                    # was 'Forward Active Energy'
                "addr": 0x000A+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kWh",
                "device_class": DeviceClass.ENERGY,
                "multiplier": ENERGY_MULTIPLIER,
                'state_class': 'total'
            },
            "Total Grid Import": {                    # was 'Reverse Active Energy'
                "addr": 0x0014+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kWh",
                "device_class": DeviceClass.ENERGY,
                "multiplier": ENERGY_MULTIPLIER,
                'state_class': 'total'
            },
            "Reverse Reactive Energy": {
                "addr": 0x0028+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kvarh",
                "device_class": DeviceClass.REACTIVE_ENERGY,
                "multiplier": ENERGY_MULTIPLIER
            },
            "Forward Reactive Energy": {
                "addr": 0x0032+1,
                "count": 2,
                "register_type": RegisterTypes.HOLDING_REGISTER,
                "dtype": DataType.I32,
                "unit": "kvarh",
                "device_class": DeviceClass.REACTIVE_ENERGY,
                "multiplier": ENERGY_MULTIPLIER
            }
        }
        if meter_reverse_connection:
            relevant_registers.update(reverse_energy_params)
            logger.info("Swopped Import and Export Energy Registers")
        else: 
            relevant_registers.update(forward_energy_params)

        return relevant_registers
    # write_parameters = {}

    # override
    @classmethod
    def from_ServerOptions(
        cls,
        opts: ServerOptions | SungrowMeterOptions, # opts will be SungrowMeterOptions if config has the ratios
        clients: list[Client]
    ):
        name = opts.name
        serial = opts.serialnum
        modbus_id: int = opts.modbus_id

        try:
            # Find the client instance this server connects to
            client_match = [c for c in clients if str(c) == opts.connected_client]
            if not client_match:
                raise ValueError(
                    f"Client '{opts.connected_client}' for server '{name}' not found in defined clients."
                )
            connected_client = client_match[0]
        except ValueError as e:
            logger.error(e)
            raise

        pt_ratio_val = None
        ct_ratio_val = None
        meter_reverse_connection = None

        # Check if the options object has the specific ratios
        if isinstance(opts, SungrowMeterOptions):
            pt_ratio_val = opts.pt_ratio
            ct_ratio_val = opts.ct_ratio
            meter_reverse_connection = opts.meter_reverse_connection
            logger.info(f"Instantiating AcrelMeter '{name}' with PT_RATIO={pt_ratio_val}, CT_RATIO={ct_ratio_val} from SungrowMeterOptions.")
            logger.info(f"Meter Reverse Connection: {meter_reverse_connection is not None and meter_reverse_connection}")
        else:
            logger.warning(
                f"AcrelMeter '{name}' is being instantiated without explicit PT/CT ratios from config. "
            )

        # Pass extracted ratios (or None) as keyword arguments to the constructor
        return cls(
            name,
            serial,
            modbus_id,
            connected_client,
            PT_RATIO=pt_ratio_val, # Pass as kwargs
            CT_RATIO=ct_ratio_val,  # Pass as kwargs
            meter_reverse_connection=meter_reverse_connection
        )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)
        self._supported_models = ('DTSD1352', ) 
        self._manufacturer = "Acrel"
        self._write_parameters: dict = dict()
        self.serial = 'unknown'
        self.device_info:dict | None = None

        # Meter-specific config
        PT_RATIO = kwargs.get("PT_RATIO")
        if PT_RATIO is None:
            raise ValueError("No PT Ratio Specified for Sungrow Meter") # Voltage Transfer
        CT_RATIO = kwargs.get("CT_RATIO") 
        if CT_RATIO is None:
            raise ValueError("No CT Ratio Specified for Sungrow Meter") # Current Transfer
        reverse_multiplier = 1
        meter_reverse_connection = kwargs.get("meter_reverse_connection") 
        if meter_reverse_connection is not None and meter_reverse_connection:
            reverse_multiplier = -1
            logger.info(f"Invert Power Measurements for reverse connection.")
        logger.info(f"Meter : {PT_RATIO=}; {CT_RATIO=}, {meter_reverse_connection=}")
        VOLTAGE_MULTIPLIER = 0.1 * PT_RATIO
        CURRENT_MULTIPLIER = 0.01 * CT_RATIO
        POWER_MULTIPLIER = 0.001 * PT_RATIO * CT_RATIO * reverse_multiplier
        ENERGY_MULTIPLIER = 0.01 * PT_RATIO * CT_RATIO
        self._parameters = AcrelMeter.get_registers(VOLTAGE_MULTIPLIER, CURRENT_MULTIPLIER, POWER_MULTIPLIER, ENERGY_MULTIPLIER, meter_reverse_connection)


    @property
    def manufacturer(self):
        return self._manufacturer
    @property
    def parameters(self):
        return self._parameters
    
    @property
    def write_parameters(self):
        return self._write_parameters

    @property
    def supported_models(self):
        return self._supported_models

    def read_model(self):
        return self.supported_models[0]
    
    def setup_valid_registers_for_model(self):
        # only support logger 1000 for now
        return
    
    def is_available(self, register_name="Phase A Voltage"):
        return super().is_available(register_name=register_name)
    
    @staticmethod
    def _decoded(registers, dtype):
        def _decode_u16(registers):
            """ Unsigned 16-bit big-endian to int """
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.UINT16)
        
        def _decode_s16(registers):
            """ Signed 16-bit big-endian to int """
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.INT16)

        def _decode_u32(registers):
            """ Unsigned 32-bit big-endian word"""
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.UINT32)
        
        def _decode_s32(registers):
            """ Signed 32-bit mixed-endian word"""
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.INT32)

        def _decode_utf8(registers):
            return ModbusSerialClient.convert_from_registers(registers=registers, data_type=ModbusSerialClient.DATATYPE.STRING)

        if dtype == DataType.UTF8: return _decode_utf8(registers)
        elif dtype == DataType.U16: return _decode_u16(registers)
        elif dtype == DataType.U32: return _decode_u32(registers)
        elif dtype == DataType.I16: return _decode_s16(registers)
        elif dtype == DataType.I32: return _decode_s32(registers)
        else: raise NotImplementedError(f"Data type {dtype} decoding not implemented")
        
    @staticmethod
    def _encoded(value, dtype):
        pass
   
    def _validate_write_val(self, register_name:str, val):
        raise NotImplementedError()
    

if __name__ == "__main__":
    print(AcrelMeter.__dict__)
    # server = AcrelMeter.from_config({})
    # if not server.model or not server.manufacturer or not server.serialnum or not server.nickname or not server.registers: 
