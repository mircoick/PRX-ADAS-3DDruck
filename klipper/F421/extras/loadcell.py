import logging
from . import bus
from . import i2c_bus_manager

LOAD_CELLS = {}

class LoadCellSensor:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]

        self.i2c_addr = config.getint("i2c_addr", 0x49)
        self.poll_time = config.getfloat("poll_time", 0.1)

        self.last_raw_bytes = (0, 0, 0)
        self.last_raw_value = 0
        self.current_weight = 0.0
        self.last_maximum = None

        self.log_counter = 0

        self.i2c = bus.MCU_I2C_from_config(
            config,
            default_addr=self.i2c_addr,
            default_speed=10000
        )

        self.reactor = self.printer.get_reactor()
        LOAD_CELLS[self.name] = self

        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )

        logging.info(
            "Loadcell INIT: name=%s, Adresse=0x%02X, poll_time=%.3f",
            self.name, self.i2c_addr, self.poll_time
        )

    def _handle_connect(self):
        delay = 1.0
        if self.i2c_addr == 0x4A:
            delay += 0.05

        self.reactor.register_timer(
            self._poll_timer,
            self.reactor.monotonic() + delay
        )

    def acquire_i2c_bus(self):
        return i2c_bus_manager.acquire(
            "LoadCell_" + self.name
        )

    def release_i2c_bus(self):
        i2c_bus_manager.release(
            "LoadCell_" + self.name
        )

    def _detect_maximum(self, b0, b1, b2):
        if (b0, b1, b2) == (0x80, 0x00, 0x9F) or (b0, b1, b2) == (0x7F, 0xFF, 0x9F):
            return "MAXIMUM"

        return None

    def _poll_timer(self, eventtime):
        owner = "LoadCell_" + self.name

        if i2c_bus_manager.is_busy_by_other(owner):
            return eventtime + self.poll_time

        if not self.acquire_i2c_bus():
            return eventtime + self.poll_time

        try:
            self.i2c.i2c_write([0xFF])
            raw = self.i2c.i2c_read([], 3)
            byte_list = self._extract_bytes(raw)

            if len(byte_list) >= 3:
                b0, b1, b2 = byte_list[:3]

                self.last_raw_bytes = (b0, b1, b2)
                self.last_raw_value = (
                    (b0 << 16) | (b1 << 8) | b2
                )

                maximum = self._detect_maximum(b0, b1, b2)

                if maximum is not None:
                    # Nur beim Wechsel in einen anderen Zustand melden.
                    if maximum != self.last_maximum:
                        logging.info(
                            "Loadcell %s (I2C 0x%02X): "
                            "%s erkannt, Bytes=%02X %02X %02X",
                            self.name,
                            self.i2c_addr,
                            maximum,
                            b0, b1, b2
                        )

                    self.last_maximum = maximum
                else:
                    self.last_maximum = None

                self.log_counter += 1

        except Exception as e:
            logging.exception(
                "Loadcell %s (I2C 0x%02X): Lesefehler",
                self.name, self.i2c_addr
            )

        finally:
            self.release_i2c_bus()

        return eventtime + self.poll_time

    def get_status(self, eventtime):
        b0, b1, b2 = self.last_raw_bytes

        return {
            "weight": 0.0,
            "raw_value": self.last_raw_value,
            "raw_bytes": "%02X %02X %02X" % (b0, b1, b2),
            "maximum": self.last_maximum,
        }

    def _extract_bytes(self, data):
        if isinstance(data, dict):
            if "response" in data:
                return self._extract_bytes(data["response"])

            if "data" in data:
                return self._extract_bytes(data["data"])

            result = []
            for key, value in data.items():
                if key not in ("oid", "#name", "params"):
                    result.extend(self._extract_bytes(value))
            return result

        if isinstance(data, (bytes, bytearray)):
            return list(data)

        if isinstance(data, (list, tuple)):
            result = []
            for item in data:
                result.extend(self._extract_bytes(item))
            return result

        if isinstance(data, int):
            return [data]

        return []


def cmd_QUERY_LOADCELL(gcmd):
    name = gcmd.get("NAME", "").strip()

    if not name:
        raise gcmd.error(
            "NAME fehlt. Verfügbar: %s"
            % ", ".join(sorted(LOAD_CELLS.keys()))
        )

    sensor = LOAD_CELLS.get(name)

    if sensor is None:
        raise gcmd.error(
            "Loadcell '%s' nicht gefunden. Registriert: %s"
            % (name, ", ".join(sorted(LOAD_CELLS.keys())))
        )

    b0, b1, b2 = sensor.last_raw_bytes

    maximum = sensor.last_maximum or "Kein Maximum erkannt"

    gcmd.respond_info(
        "Loadcell %s (I2C 0x%02X): "
        "Bytes=%02X %02X %02X | raw24=0x%06X | Status=%s"
        % (
            sensor.name,
            sensor.i2c_addr,
            b0, b1, b2,
            sensor.last_raw_value,
            maximum
        )
    )


def load_config_prefix(config):
    printer = config.get_printer()

    if not hasattr(printer, "_query_loadcell_registered"):
        gcode = printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_LOADCELL",
            cmd_QUERY_LOADCELL,
            desc="Zeigt Rohdaten und Maximum-Status einer Loadcell"
        )
        printer._query_loadcell_registered = True

    return LoadCellSensor(config)
