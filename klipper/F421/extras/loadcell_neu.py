# loadcell.py - Erweitert mit Lastzellen-Mesh-Kalibrierung und Taring
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
        self.trigger_threshold = config.getint("trigger_threshold", 50000) # Kraft-Differenz für Kontakterkennung
        self.z_hop = config.getfloat("z_hop", 5.0)
        self.probe_speed = config.getfloat("probe_speed", 5.0) # mm/s für die Z-Suche

        self.last_raw_bytes = (0, 0, 0)
        self.last_raw_value = 0
        self.baseline_value = 0
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
            "Loadcell INIT: name=%s, Adresse=0x%02X, poll_time=%.3f, threshold=%d",
            self.name, self.i2c_addr, self.poll_time, self.trigger_threshold
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

    def read_immediate(self):
        """Liest den Sensor direkt unter Berücksichtigung des I2C-Bus-Managers aus."""
        owner = "LoadCell_" + self.name
        waited = 0
        while i2c_bus_manager.is_busy_by_other(owner) and waited < 0.5:
            self.reactor.pause(self.reactor.monotonic() + 0.01)
            waited += 0.01

        if not self.acquire_i2c_bus():
            return self.last_raw_value

        try:
            self.i2c.i2c_write([0xFF])
            raw = self.i2c.i2c_read([], 3)
            byte_list = self._extract_bytes(raw)
            if len(byte_list) >= 3:
                b0, b1, b2 = byte_list[:3]
                self.last_raw_bytes = (b0, b1, b2)
                self.last_raw_value = ((b0 << 16) | (b1 << 8) | b2)
        except Exception:
            pass
        finally:
            self.release_i2c_bus()

        return self.last_raw_value

    def tare(self):
        """Setzt den aktuellen Messwert als Nullpunkt (Baseline)."""
        self.baseline_value = self.read_immediate()
        logging.info("Loadcell %s getart: Baseline = 0x%06X", self.name, self.baseline_value)

    def check_triggered(self):
        """Prüft, ob die Lastzelle berührt wurde (Wert weicht stärker als Schwellenwert ab)."""
        current = self.read_immediate()
        diff = abs(current - self.baseline_value)
        return diff >= self.trigger_threshold, diff

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
                self.last_raw_value = ((b0 << 16) | (b1 << 8) | b2)

                maximum = self._detect_maximum(b0, b1, b2)

                if maximum is not None:
                    if maximum != self.last_maximum:
                        logging.info(
                            "Loadcell %s (I2C 0x%02X): %s erkannt, Bytes=%02X %02X %02X",
                            self.name, self.i2c_addr, maximum, b0, b1, b2
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
            "baseline": self.baseline_value,
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
        raise gcmd.error("NAME fehlt. Verfügbar: %s" % ", ".join(sorted(LOAD_CELLS.keys())))
    sensor = LOAD_CELLS.get(name)
    if sensor is None:
        raise gcmd.error("Loadcell '%s' nicht gefunden." % name)

    b0, b1, b2 = sensor.last_raw_bytes
    maximum = sensor.last_maximum or "Kein Maximum erkannt"
    gcmd.respond_info(
        "Loadcell %s (I2C 0x%02X): Bytes=%02X %02X %02X | raw24=0x%06X | Baseline=0x%06X | Status=%s"
        % (sensor.name, sensor.i2c_addr, b0, b1, b2, sensor.last_raw_value, sensor.baseline_value, maximum)
    )


def cmd_TARE_LOADCELL(gcmd):
    name = gcmd.get("NAME", "").strip()
    if name:
        sensor = LOAD_CELLS.get(name)
        if sensor:
            sensor.tare()
            gcmd.respond_info("Loadcell '%s' getart (Nullpunkt gesetzt)." % name)
        else:
            raise gcmd.error("Loadcell '%s' nicht gefunden." % name)
    else:
        for s in LOAD_CELLS.values():
            s.tare()
        gcmd.respond_info("Alle Loadcells getart.")


def cmd_LOADCELL_MESH_CALIBRATE(gcmd):
    printer = gcmd.get_printer()
    toolhead = printer.lookup_object('toolhead')
    
    # Wähle die zu verwendende Lastzelle (Standard: loadcell_l)
    sensor_name = gcmd.get("SENSOR", "loadcell_l" if "loadcell_l" in LOAD_CELLS else list(LOAD_CELLS.keys())[0])
    sensor = LOAD_CELLS.get(sensor_name)
    if not sensor:
        raise gcmd.error("Keine Loadcell für die Mesh-Kalibrierung verfügbar!")

    gcmd.respond_info("Starte Lastzellen-Mesh-Kalibrierung mit Sensor: %s" % sensor.name)
    
    # Vor Beginn Nullpunkt tarieren
    sensor.tare()

    # Beispielhafte Messpunkte (können flexibel erweitert werden)
    probe_points = [
        (50, 50), (100, 50), (150, 50),
        (150, 100), (100, 100), (50, 100)
    ]

    z_results = []
    for pt in probe_points:
        # 1. Zu X/Y Position fahren
        toolhead.manual_move([pt[0], pt[1], None], 100)
        toolhead.wait_moves()
        
        # Vor jedem Punkt kurz tarieren, um Drift auszugleichen
        sensor.tare()

        # 2. Z langsam absenken und auf Auslösung prüfen
        pos = toolhead.get_position()
        target_z = max(0.0, pos[2] - 15.0) # Suchweg nach unten
        step = 0.05 # 0.05 mm Schritte
        
        current_z = pos[2]
        triggered = False
        
        while current_z > target_z:
            current_z -= step
            toolhead.manual_move([None, None, current_z], sensor.probe_speed)
            toolhead.wait_moves()
            
            is_trg, diff = sensor.check_triggered()
            if is_trg:
                triggered = True
                break
        
        if triggered:
            hit_z = toolhead.get_position()[2]
            gcmd.respond_info("Punkt X=%.1f Y=%.1f gemessen bei Z=%.3f (Diff: %d)" % (pt[0], pt[1], hit_z, diff))
            z_results.append((pt[0], pt[1], hit_z))
        else:
            gcmd.respond_info("Fehler: Lastzelle an Punkt X=%.1f Y=%.1f nicht ausgelöst!" % (pt[0], pt[1]))
            
        # 3. Z-Hop nach oben
        toolhead.manual_move([None, None, toolhead.get_position()[2] + sensor.z_hop], 50)
        toolhead.wait_moves()

    gcmd.respond_info("Lastzellen-Mesh abgeschlossen. Erfasste Punkte: %s" % z_results)


def load_config_prefix(config):
    printer = config.get_printer()

    if not hasattr(printer, "_loadcell_commands_registered"):
        gcode = printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_LOADCELL",
            cmd_QUERY_LOADCELL,
            desc="Zeigt Rohdaten und Status einer Loadcell"
        )
        gcode.register_command(
            "TARE_LOADCELL",
            cmd_TARE_LOADCELL,
            desc="Nullpunkt (Baseline) der Lastzellen setzen"
        )
        gcode.register_command(
            "LOADCELL_MESH_CALIBRATE",
            cmd_LOADCELL_MESH_CALIBRATE,
            desc="Führt eine Mesh-Messung über die Lastzellen aus"
        )
        printer._loadcell_commands_registered = True

    return LoadCellSensor(config)