# Changelog

## 0.5.4

### Added
- Logger PT100 temperature inputs `PT100-1 temperature` (8027) and `PT100-2 temperature` (8028), S16 at 0.1 °C. Per the logger protocol these exist only on Logger3000/Logger4000, so `setup_valid_registers_for_model()` drops them on any other model. The add-on's `supported_models` is still Logger1000-only, so these stay inert until a Logger3000/4000 is enabled.

### Fixed
- `SungrowLogger._parameters` aliased the class-level `logger_input_registers` dict instead of copying it, so any per-model register removal would have mutated the map shared by every logger instance. Now a copy, matching `_write_parameters`.

## 0.5.3

### Fixed
- Reconnecting to a Sungrow inverter always raised `KeyError` and never succeeded. `setup_valid_registers_for_model()` runs on the initial connect *and* on every reconnect, but removed model-unsupported registers with a bare `dict.pop()`, so the second call failed on registers the first had already removed. Register setup is now idempotent.

  On 0.5.1 this killed the addon outright: the reconnect sweep caught only `ConnectionError`, so the `KeyError` escaped the read loop and the exit handler published a retained `offline` to the bridge availability topic. Because every entity is discovered with `availability_mode: all` against that topic, one inverter blip took *all* of the addon's entities unavailable at once — inverters, meter and logger — and they stayed that way until the addon next started cleanly. 0.5.2's broad `except` in the sweep stopped the crash but left the `KeyError`, so the device instead stayed permanently in the disconnected list. This release fixes the cause.

## 0.5.2

### Fixed
- Unrecoverable reconnect loop after the device closed the TCP connection: the stale socket was never closed, so every retry reused it and only a manual addon restart recovered. Connection errors now force a fresh socket and retry once before escalating.
- Modbus timeouts (slow device) no longer tear down the transport; they get one in-place retry before escalating, preventing availability flapping and serial-port churn on RTU.
- Reconnect attempts to offline devices are paced by a 30s cooldown instead of retrying every loop.
- MQTT discovery is republished when a server reconnects, so devices that were offline at addon startup now get their Home Assistant entities.
- A failed reconnect during the retry sweep can no longer crash the addon; the addon also starts (and keeps retrying) when all devices are offline at boot.
- Modbus access is serialised between the read loop and the MQTT command thread.
