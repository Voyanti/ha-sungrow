import unittest
from src.enums import DataType
from src.sungrow_inverter import SungrowInverter


class TestSungrowInverterCoding(unittest.TestCase):
    """Decode/encode go through the _decoded/_encoded dispatchers; the per-type
    helpers are nested inside _decoded and cannot be reached directly."""

    def test_decode_u16(self):
        self.assertEqual(SungrowInverter._decoded([258], DataType.U16), 258)

    def test_decode_u32_mixed_endian(self):
        # low word first: [0x0304, 0x0102] -> 0x01020304
        self.assertEqual(SungrowInverter._decoded([772, 258], DataType.U32), 16909060)

    def test_decode_utf8(self):
        self.assertEqual(
            SungrowInverter._decoded([16706, 17220, 17734, 18248, 18762], DataType.UTF8),
            "ABCDEFGHIJ")

    def test_decode_i16(self):
        self.assertEqual(SungrowInverter._decoded([2**15 - 1], DataType.I16), -32769)
        self.assertEqual(SungrowInverter._decoded([2**16 - 1], DataType.I16), -1)

    def test_decode_i32(self):
        self.assertEqual(SungrowInverter._decoded([65535, 65535], DataType.I32), -1)
        # [0x777B, 0xFFFF] -> 0xFFFF777B -> -34949
        self.assertEqual(SungrowInverter._decoded([30587, 65535], DataType.I32), -34949)

    def test_decode_unsupported_dtype(self):
        self.assertRaises(NotImplementedError,
                          SungrowInverter._decoded, [0, 0, 0, 0], DataType.U64)

    def test_encode_u16(self):
        self.assertEqual(SungrowInverter._encoded(2**16 - 1, DataType.U16), [65535])
        self.assertEqual(SungrowInverter._encoded(0, DataType.U16), [0])
        self.assertEqual(SungrowInverter._encoded(12.7, DataType.U16), [12])

    def test_encode_rejects_out_of_range(self):
        self.assertRaisesRegex(ValueError, r"negative value=-1",
                               SungrowInverter._encoded, -1, DataType.U16)
        self.assertRaisesRegex(ValueError, r"value=65536",
                               SungrowInverter._encoded, 2**16, DataType.U16)


class TestSungrowInverterRegisterSetup(unittest.TestCase):

    def _inverter(self, model="SG125CX-P2", mppt=1):
        inv = SungrowInverter(name="Sungrow1", serial="A2462500663",
                              modbus_id=2, connected_client=None)
        inv.model = model
        inv.model_info = {"mppt": mppt}
        # setup_valid_registers_for_model reads "Output Type" off the wire
        inv.read_registers = lambda name: 1
        return inv

    def test_drops_registers_unsupported_by_model(self):
        inv = self._inverter()
        inv.setup_valid_registers_for_model()
        # SG125CX-P2 is absent from these registers' supported-model lists
        for name in ("Total Power Yields (Increased Accuracy)",
                     "Grid Frequency (Increased Accuracy)"):
            self.assertNotIn(name, inv.parameters)

    def test_is_idempotent(self):
        """Regression: connect() calls this again on every reconnect. A bare
        dict.pop() raised KeyError the second time round, which in 0.5.1 escaped
        the reconnect sweep and killed the addon -- taking every entity
        unavailable via the bridge Last Will, not just the one device."""
        inv = self._inverter()
        inv.setup_valid_registers_for_model()
        first = dict(inv.parameters)
        inv.setup_valid_registers_for_model()   # must not raise
        self.assertEqual(first, inv.parameters)


if __name__ == "__main__":
    unittest.main()
