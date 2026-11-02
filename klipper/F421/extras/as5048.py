
import logging
from . import bus
from . import i2c_bus_manager

logging.warning("AS5048 MODULE FILE LOADED")
AS5048_SENSORS = {}


class AS5048Sensor:
    REG_ANGLE_HIGH = 0xFE
    REG_ANGLE_LOW = 0xFF
    REG_DIAGNOSTICS = 0xFB
    REG_MAGNITUDE_HIGH = 0xFC
    REG_MAGNITUDE_LOW = 0xFD
    REG_AGC = 0xFA

    RESOLUTION = 16384
    MAX_ANGLE = RESOLUTION - 1

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]

        self.i2c_addr = config.getint("i2c_addr", 0x40)
        if self.i2c_addr not in (0x40, 0x41):
            raise config.error(
                "AS5048 %s: i2c_addr muss 0x40 oder 0x41 sein"
                % self.name
            )

        self.poll_time = config.getfloat(
            "poll_time", 0.15, minval=0.15        )

        # Letzte Messwerte
        self.last_raw_bytes = (0, 0)
        self.raw_angle = 0
        self.angle_deg = 0.0

        self.last_diagnostics = None
        self.last_magnitude = None
        self.last_agc = None
        self.last_error = None
        self.read_count = 0

        self.i2c = bus.MCU_I2C_from_config(
            config,
            default_addr=self.i2c_addr,
            default_speed=100000
        )

        self.reactor = self.printer.get_reactor()

        AS5048_SENSORS[self.name] = self

        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )

        logging.info(
            "AS5048 INIT: name=%s, Adresse=0x%02X, "
            "poll_time=%.3f",
            self.name, self.i2c_addr, self.poll_time
        )

    def _handle_connect(self):
        # Sensoren mit leichtem zeitlichen Versatz starten.
        delay = 1.0
        if self.i2c_addr == 0x41:
            delay += 0.025

        self.reactor.register_timer(
            self._poll_timer,
            self.reactor.monotonic() + delay
        )

    def acquire_i2c_bus(self):
        return i2c_bus_manager.acquire(
            "AS5048_" + self.name
        )

    def release_i2c_bus(self):
        i2c_bus_manager.release(
            "AS5048_" + self.name
        )

    def _read_register(self, register, length):
        # Registeradresse senden, anschließend Daten lesen.
        self.i2c.i2c_write([register])
        return self._extract_bytes(
            self.i2c.i2c_read([], length)
        )

    def _read_angle(self):
        data = self._extract_bytes(
            self.i2c.i2c_read([0xFE], 2)
        )

        if len(data) < 2:
            raise RuntimeError(
                "Ungültige Winkelantwort: %s" % data
            )

        high, low = data[:2]
        raw = ((high << 6) | (low & 0x3F)) & 0x3FFF
        angle = raw * 360.0 / 16384.0

        return high, low, raw, angle

    def _read_diagnostics(self):
        data = self._read_register(
            self.REG_DIAGNOSTICS, 1
        )
        if not data:
            raise RuntimeError(
                "Keine Diagnoseantwort erhalten"
            )
        return data[0]

    def _read_magnitude(self):
        data = self._read_register(
            self.REG_MAGNITUDE_HIGH, 2
        )
        if len(data) < 2:
            raise RuntimeError(
                "Ungültige Magnetfeldantwort"
            )

        return (
            (data[0] << 6) | (data[1] & 0x3F)
        ) & 0x3FFF

    def _read_agc(self):
        data = self._read_register(self.REG_AGC, 1)
        if not data:
            raise RuntimeError(
                "Keine AGC-Antwort erhalten"
            )
        return data[0]

    def _poll_timer(self, eventtime):
        owner = "AS5048_" + self.name

        if i2c_bus_manager.is_busy_by_other(owner):
            return eventtime + self.poll_time

        if not self.acquire_i2c_bus():
            return eventtime + self.poll_time

        try:
            high, low, raw, angle = self._read_angle()

            self.last_raw_bytes = (high, low)
            self.raw_angle = raw
            self.angle_deg = angle
            self.last_error = None
            self.read_count += 1

            # Diagnose und Magnetfeldwerte separat lesen.
            # Ein Fehler hierbei soll den gültigen Winkel
            # nicht verwerfen.
            try:
                self.last_diagnostics = (
                    self._read_diagnostics()
                )
                self.last_magnitude = (
                    self._read_magnitude()
                )
                self.last_agc = self._read_agc()
            except Exception:
                logging.debug(
                    "AS5048 %s: Diagnose nicht verfügbar",
                    self.name,
                    exc_info=True
                )

        except Exception as e:
            self.last_error = str(e)
            logging.exception(
                "AS5048 %s (I2C 0x%02X): Lesefehler",
                self.name, self.i2c_addr
            )

        finally:
            self.release_i2c_bus()

        return eventtime + self.poll_time

    def get_status(self, eventtime):
        high, low = self.last_raw_bytes
        diagnostics = self.last_diagnostics

        return {
            "name": self.name,
            "i2c_address": self.i2c_addr,
            "angle": round(self.angle_deg, 4),
            "raw_angle": self.raw_angle,
            "raw_bytes": "%02X %02X" % (high, low),
            "diagnostics": diagnostics,
            "magnet_status": (
                self._format_diagnostics(diagnostics)
            ),
            "magnitude": self.last_magnitude,
            "agc": self.last_agc,
            "read_count": self.read_count,
            "error": self.last_error,
        }

    def _format_diagnostics(self, value):
        if value is None:
            return "unbekannt"

        flags = []

        if value & 0x08:
            flags.append("COMP_HIGH")
        if value & 0x04:
            flags.append("COMP_LOW")
        if value & 0x02:
            flags.append("CORDIC_OVERFLOW")
        if not (value & 0x01):
            flags.append("OFFSET_COMP_NOT_READY")

        if not flags:
            return "OK"

        return ",".join(flags)

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



def cmd_QUERY_AS5048(gcmd):
    name = gcmd.get("NAME", "").strip()
    sensor = AS5048_SENSORS.get(name)

    if sensor is None:
        raise gcmd.error(
            "AS5048 '%s' nicht gefunden. Registriert: %s"
            % (name, ", ".join(sorted(AS5048_SENSORS.keys())))
        )

    high, low = sensor.last_raw_bytes

    gcmd.respond_info(
        "AS5048 %s (I2C 0x%02X): Winkel=%.4f Grad | "
        "raw14=0x%04X | Bytes=%02X %02X | "
        "Magnetfeld=%s | Magnitude=%s | AGC=%s"
        % (
            sensor.name,
            sensor.i2c_addr,
            sensor.angle_deg,
            sensor.raw_angle,
            high,
            low,
            sensor._format_diagnostics(sensor.last_diagnostics),
            str(sensor.last_magnitude),
            str(sensor.last_agc),
        )
    )


def load_config_prefix(config):
    printer = config.get_printer()

    if not hasattr(printer, "_query_AS5048_registered"):
        gcode = printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_AS5048",
            cmd_QUERY_AS5048,
            desc="Zeigt Winkel und Status eines AS5048"
        )
        printer._query_AS5048_registered = True
        logging.info("AS5048: G-Code QUERY_AS5048 registriert")

    return AS5048Sensor(config)