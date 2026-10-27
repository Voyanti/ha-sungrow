import unittest

from src.sungrow_logger import SungrowLogger


class TestLoggerPT100(unittest.TestCase):
    """PT100-1/2 exist only on Logger3000/Logger4000; the register map must be
    per-instance and the removal must survive a reconnect (setup runs again)."""

    def _logger(self, model: str) -> SungrowLogger:
        server = SungrowLogger("logger", "serial", 247, None)
        server.model = model
        return server

    def test_parameters_are_not_the_shared_class_dict(self):
        server = self._logger("Logger1000")
        self.assertIsNot(server._parameters, SungrowLogger.logger_input_registers)

    def test_dropped_on_logger1000_and_idempotent(self):
        server = self._logger("Logger1000")
        server.setup_valid_registers_for_model()
        server.setup_valid_registers_for_model()
        self.assertNotIn("PT100-1 temperature", server._parameters)
        self.assertNotIn("PT100-2 temperature", server._parameters)
        self.assertIn("PT100-1 temperature", SungrowLogger.logger_input_registers)

    def test_kept_on_logger3000(self):
        server = self._logger("Logger3000")
        server.setup_valid_registers_for_model()
        self.assertEqual(server._parameters["PT100-1 temperature"]["addr"], 8027)
        self.assertEqual(server._parameters["PT100-2 temperature"]["addr"], 8028)


if __name__ == "__main__":
    unittest.main()
