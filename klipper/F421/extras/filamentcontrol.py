import logging
from . import bus
from . import i2c_bus_manager


FILAMENT_DRIVERS = {}


FILAMENT_ORDER = [
    "Model_1",
    "Model_2",
    "Support_3",
    "Support_4",
]


# ------------------------------------------------------------
# AUTO LOAD ZEITEN
# ------------------------------------------------------------

LOAD_TIMES = {
    "Model_1": {
        0x64: 53.0,
    },

    "Model_2": {
        0x64: 45.0,
    },

    "Support_3": {
        0x64: 35.0,
    },

    "Support_4": {
        0x64: 35.0,
    },
}


# ------------------------------------------------------------
# AUTO UNLOAD
# ------------------------------------------------------------

UNLOAD_MAX_TIME = 120.0
UNLOAD_POLL_TIME = 0.05


# ============================================================
# FILAMENT DRIVER
# ============================================================

class FilamentDriver:

    def __init__(self, config):

        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]

        self.i2c_addr = config.getint(
            'i2c_addr',
            0x6C
        )

        self.poll_time = config.getfloat(
            'poll_time',
            0.5
        )

        self.run_duration = config.getfloat(
            'run_duration',
            2.0
        )

        self.run_direction = config.get(
            'run_direction',
            'for'
        )

        self.speed = config.getint(
            'speed',
            0x64
        )

        self.i2c = bus.MCU_I2C_from_config(
            config,
            default_addr=self.i2c_addr,
            default_speed=10000
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.last_filament_state = 0x01

        self.is_running = False

        self.operation = None

        self.operation_end_time = None
        self.operation_start_time = None

        self.unload_timeout = False

        # ----------------------------------------------------
        # REACTOR
        # ----------------------------------------------------

        self.reactor = self.printer.get_reactor()

        # ----------------------------------------------------
        # GLOBAL REGISTRY
        # ----------------------------------------------------

        FILAMENT_DRIVERS[self.name] = self

        # ----------------------------------------------------
        # CONNECT
        # ----------------------------------------------------

        self.printer.register_event_handler(
            "klippy:connect",
            self._handle_connect
        )

        # ----------------------------------------------------
        # GCODE
        # ----------------------------------------------------

        gcode = self.printer.lookup_object('gcode')

        try:

            gcode.register_command(
                "FEED_FILAMENT",
                self.cmd_FEED_FILAMENT,
                desc="Manuelle Filamentbewegung"
            )

        except Exception:
            pass

        try:

            gcode.register_command(
                "QUERY_FILAMENT",
                self.cmd_QUERY_FILAMENT,
                desc="Zeigt den Filamentsensor-Status an"
            )

        except Exception:
            pass

        try:

            gcode.register_command(
                "AUTO_LOAD",
                self.cmd_AUTO_LOAD,
                desc="Automatisches Laden eines Filaments"
            )

        except Exception:
            pass

        try:

            gcode.register_command(
                "AUTO_UNLOAD",
                self.cmd_AUTO_UNLOAD,
                desc="Automatisches Entladen eines Filaments"
            )

        except Exception:
            pass

    # ========================================================
    # CONNECT
    # ========================================================

    def _handle_connect(self):

        self.reactor.register_timer(
            self._check_sensor_timer,
            self.reactor.monotonic() + 1.0
        )

    # ========================================================
    # I2C BUS
    # ========================================================

    def acquire_i2c_bus(self):

        if not i2c_bus_manager.acquire(self.name):

            logging.warning(
                "%s: I2C-Bus ist bereits durch %s belegt.",
                self.name,
                i2c_bus_manager.get_owner()
            )

            return False

        logging.debug(
            "%s: I2C-Bus übernommen.",
            self.name
        )

        return True

    def release_i2c_bus(self):

        i2c_bus_manager.release(self.name)

        logging.debug(
            "%s: I2C-Bus freigegeben.",
            self.name
        )

    # ========================================================
    # I2C WRITE
    # ========================================================

    def write_reg(self, reg, val):

        try:

            self.i2c.i2c_write(
                [reg, val]
            )

            return True

        except Exception as e:

            logging.debug(
                "I2C Write Fehler (%s) "
                "Reg 0x%02X: %s",
                self.name,
                reg,
                str(e)
            )

            return False

    # ========================================================
    # I2C READ
    # ========================================================

    def read_reg(self, reg, length=1):

        try:

            self.i2c.i2c_write(
                [reg]
            )

            raw = self.i2c.i2c_read(
                [],
                length
            )

            return self._extract_bytes(raw)

        except Exception as e:

            logging.debug(
                "I2C Read Fehler (%s) "
                "Reg 0x%02X: %s",
                self.name,
                reg,
                str(e)
            )

            return []

    # ========================================================
    # SENSOR
    # ========================================================

    def _check_sensor_timer(self, eventtime):

        # ----------------------------------------------------
        # Wenn ein anderer Filamenttreiber den Bus benutzt,
        # nicht lesen.
        # ----------------------------------------------------

        if i2c_bus_manager.is_busy_by_other(
            self.name
        ):

            return eventtime + self.poll_time

        # ----------------------------------------------------
        # Während eigener AUTO_UNLOAD-Aktion darf dieser
        # Treiber seinen Sensor weiterhin lesen.
        # ----------------------------------------------------

        byte_list = self.read_reg(
            0x03,
            1
        )

        if byte_list:

            self.last_filament_state = byte_list[0]

        return eventtime + self.poll_time

    # ========================================================
    # FILAMENT DETECTED
    # ========================================================

    def filament_detected(self):

        return self.last_filament_state == 0x03

    # ========================================================
    # QUERY FILAMENT
    # ========================================================

    def cmd_QUERY_FILAMENT(self, gcmd):

        target_name = gcmd.get(
            'NAME',
            None
        )

        if target_name:

            target_name = target_name.strip()

            driver = FILAMENT_DRIVERS.get(
                target_name
            )

            if not driver:

                gcmd.respond_error(
                    "Unbekannte Einheit '%s'. "
                    "Verfügbar: %s"
                    % (
                        target_name,
                        ', '.join(
                            FILAMENT_DRIVERS.keys()
                        )
                    )
                )

                return

            drivers_to_query = [
                driver
            ]

        else:

            drivers_to_query = list(
                FILAMENT_DRIVERS.values()
            )

        for driver in drivers_to_query:

            state = driver.last_filament_state

            if state == 0x03:

                status = "FILAMENT ERKANNT"

            elif state == 0x01:

                status = "KEIN FILAMENT"

            else:

                status = (
                    "UNBEKANNTER STATUS 0x%02X"
                    % state
                )

            gcmd.respond_info(
                "%s: %s "
                "(Register 0x03 = 0x%02X)"
                % (
                    driver.name,
                    status,
                    state
                )
            )

    # ========================================================
    # MOTOR START
    # ========================================================

    def start_motor(
        self,
        direction,
        speed
    ):

        if self.is_running:

            return False

        direction = direction.strip().lower()

        if direction == "back":

            if not self.write_reg(
                0x06,
                speed
            ):

                return False

            if not self.write_reg(
                0x0A,
                0x02
            ):

                return False

        elif direction == "for":

            if not self.write_reg(
                0x05,
                speed
            ):

                return False

            if not self.write_reg(
                0x0A,
                0x01
            ):

                return False

        else:

            logging.error(
                "%s: Ungültige Richtung %s",
                self.name,
                direction
            )

            return False

        self.is_running = True

        return True

    # ========================================================
    # MOTOR STOP
    # ========================================================

    def stop_motor(self):

        try:

            self.write_reg(
                0x0A,
                0x00
            )

        finally:

            self.is_running = False

    # ========================================================
    # FEED TIMER
    # ========================================================

    def _feed_timer(self, eventtime):

        if not self.is_running:

            self.release_i2c_bus()

            return self.reactor.NEVER

        if (
            self.operation_end_time is not None
            and eventtime >= self.operation_end_time
        ):

            self.stop_motor()

            self.operation = None
            self.operation_end_time = None
            self.operation_start_time = None

            self.release_i2c_bus()

            if self._feed_gcmd:

                self._feed_gcmd.respond_info(
                    "%s: Motor gestoppt.",
                    self.name
                )

            self._feed_gcmd = None

            return self.reactor.NEVER

        return eventtime + 0.05

    # ========================================================
    # START TIMED MOTOR
    # ========================================================

    def start_timed_motor(
        self,
        direction,
        duration,
        speed,
        gcmd=None
    ):

        if self.is_running:

            return False

        if not self.acquire_i2c_bus():

            return False

        if not self.start_motor(
            direction,
            speed
        ):

            self.release_i2c_bus()

            return False

        self.operation = "feed"

        self.operation_start_time = (
            self.reactor.monotonic()
        )

        self.operation_end_time = (
            self.operation_start_time
            + duration
        )

        self._feed_gcmd = gcmd

        self.reactor.register_timer(
            self._feed_timer,
            self.reactor.monotonic() + 0.05
        )

        return True

    # ========================================================
    # AUTO LOAD
    # ========================================================

    def cmd_AUTO_LOAD(self, gcmd):

        target_name = gcmd.get(
            'NAME',
            None
        )

        if not target_name:

            gcmd.respond_error(
                "AUTO_LOAD benötigt NAME="
            )

            return

        target_name = target_name.strip()

        driver = FILAMENT_DRIVERS.get(
            target_name
        )

        if not driver:

            gcmd.respond_error(
                "Unbekannte Einheit '%s'. "
                "Verfügbar: %s"
                % (
                    target_name,
                    ', '.join(
                        FILAMENT_DRIVERS.keys()
                    )
                )
            )

            return

        if driver.is_running:

            gcmd.respond_error(
                "%s läuft bereits."
                % target_name
            )

            return

        speed = gcmd.get_int(
            'SPEED',
            driver.speed
        )

        if speed < 0 or speed > 255:

            gcmd.respond_error(
                "Ungültige Geschwindigkeit: %d"
                % speed
            )

            return

        duration_table = LOAD_TIMES.get(
            target_name
        )

        if not duration_table:

            gcmd.respond_error(
                "Keine Ladezeit für %s definiert."
                % target_name
            )

            return

        duration = duration_table.get(
            speed
        )

        if duration is None:

            gcmd.respond_error(
                "Keine Ladezeit für %s bei "
                "SPEED=0x%02X definiert."
                % (
                    target_name,
                    speed
                )
            )

            return

        # ----------------------------------------------------
        # BUS RESERVIEREN
        # ----------------------------------------------------

        if not driver.acquire_i2c_bus():

            gcmd.respond_error(
                "I2C-Bus ist momentan durch %s belegt."
                % i2c_bus_manager.get_owner()
            )

            return

        gcmd.respond_info(
            "AUTO_LOAD %s gestartet: "
            "%.1fs bei SPEED=0x%02X"
            % (
                target_name,
                duration,
                speed
            )
        )

        # ----------------------------------------------------
        # MOTOR STARTEN
        # ----------------------------------------------------

        if not driver.start_motor(
            "for",
            speed
        ):

            driver.release_i2c_bus()

            gcmd.respond_error(
                "AUTO_LOAD %s: Motor konnte "
                "nicht gestartet werden."
                % target_name
            )

            return

        # ----------------------------------------------------
        # STATUS SETZEN
        # ----------------------------------------------------

        driver.operation = "auto_load"

        driver.operation_start_time = (
            self.reactor.monotonic()
        )

        driver.operation_end_time = (
            driver.operation_start_time
            + duration
        )

        driver._feed_gcmd = gcmd

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        self.reactor.register_timer(
            driver._auto_load_timer,
            self.reactor.monotonic() + 0.05
        )

    # ========================================================
    # AUTO LOAD TIMER
    # ========================================================

    def _auto_load_timer(self, eventtime):

        if self.operation != "auto_load":

            return self.reactor.NEVER

        if (
            self.operation_end_time is not None
            and eventtime >= self.operation_end_time
        ):

            self.stop_motor()

            self.operation = None

            self.operation_end_time = None
            self.operation_start_time = None

            self.release_i2c_bus()

            if self._feed_gcmd:

                self._feed_gcmd.respond_info(
                    "AUTO_LOAD %s abgeschlossen."
                    % self.name
                )

            self._feed_gcmd = None

            return self.reactor.NEVER

        return eventtime + 0.05

    # ========================================================
    # AUTO UNLOAD
    # ========================================================

    def cmd_AUTO_UNLOAD(self, gcmd):

        target_name = gcmd.get(
            'NAME',
            None
        )

        if not target_name:

            gcmd.respond_error(
                "AUTO_UNLOAD benötigt NAME="
            )

            return

        target_name = target_name.strip()

        driver = FILAMENT_DRIVERS.get(
            target_name
        )

        if not driver:

            gcmd.respond_error(
                "Unbekannte Einheit '%s'. "
                "Verfügbar: %s"
                % (
                    target_name,
                    ', '.join(
                        FILAMENT_DRIVERS.keys()
                    )
                )
            )

            return

        if driver.is_running:

            gcmd.respond_error(
                "%s läuft bereits."
                % target_name
            )

            return

        speed = gcmd.get_int(
            'SPEED',
            driver.speed
        )

        if speed < 0 or speed > 255:

            gcmd.respond_error(
                "Ungültige Geschwindigkeit: %d"
                % speed
            )

            return

        # ----------------------------------------------------
        # BUS RESERVIEREN
        # ----------------------------------------------------

        if not driver.acquire_i2c_bus():

            gcmd.respond_error(
                "I2C-Bus ist momentan durch %s belegt."
                % i2c_bus_manager.get_owner()
            )

            return

        # ----------------------------------------------------
        # MOTOR STARTEN
        # ----------------------------------------------------

        if not driver.start_motor(
            "back",
            speed
        ):

            driver.release_i2c_bus()

            gcmd.respond_error(
                "AUTO_UNLOAD %s: Motor konnte "
                "nicht gestartet werden."
                % target_name
            )

            return

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        driver.operation = "auto_unload"

        driver.operation_start_time = (
            self.reactor.monotonic()
        )

        driver.operation_end_time = (
            driver.operation_start_time
            + UNLOAD_MAX_TIME
        )

        driver._feed_gcmd = gcmd

        gcmd.respond_info(
            "AUTO_UNLOAD %s gestartet. "
            "Motor läuft rückwärts bis "
            "Sensor 0x03 -> 0x01."
            % target_name
        )

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        self.reactor.register_timer(
            driver._auto_unload_timer,
            self.reactor.monotonic()
            + UNLOAD_POLL_TIME
        )

    # ========================================================
    # AUTO UNLOAD TIMER
    # ========================================================

    def _auto_unload_timer(self, eventtime):

        if self.operation != "auto_unload":

            return self.reactor.NEVER

        # ----------------------------------------------------
        # SENSOR DIREKT LESEN
        # ----------------------------------------------------

        byte_list = self.read_reg(
            0x03,
            1
        )

        if byte_list:

            state = byte_list[0]

            self.last_filament_state = state

            # ------------------------------------------------
            # FILAMENT NICHT MEHR ERKANNT
            # ------------------------------------------------

            if state == 0x01:

                self.stop_motor()

                self.operation = None

                self.operation_start_time = None
                self.operation_end_time = None

                self.release_i2c_bus()

                if self._feed_gcmd:

                    self._feed_gcmd.respond_info(
                        "AUTO_UNLOAD %s: "
                        "Filament nicht mehr erkannt."
                        % self.name
                    )

                    self._feed_gcmd.respond_info(
                        "AUTO_UNLOAD %s: "
                        "Motor gestoppt."
                        % self.name
                    )

                self._feed_gcmd = None

                return self.reactor.NEVER

        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        if (
            self.operation_end_time is not None
            and eventtime >= self.operation_end_time
        ):

            self.stop_motor()

            self.operation = None

            self.operation_start_time = None
            self.operation_end_time = None

            self.release_i2c_bus()

            if self._feed_gcmd:

                self._feed_gcmd.respond_error(
                    "AUTO_UNLOAD %s: "
                    "Timeout nach %.1fs. "
                    "Sensor meldet weiterhin Filament."
                    % (
                        self.name,
                        UNLOAD_MAX_TIME
                    )
                )

                self._feed_gcmd.respond_info(
                    "AUTO_UNLOAD %s: "
                    "Motor gestoppt."
                    % self.name
                )

            self._feed_gcmd = None

            return self.reactor.NEVER

        return eventtime + UNLOAD_POLL_TIME

    # ========================================================
    # FEED FILAMENT
    # ========================================================

    def cmd_FEED_FILAMENT(self, gcmd):

        target_name = gcmd.get(
            'NAME',
            None
        )

        duration = gcmd.get_float(
            'DURATION',
            self.run_duration
        )

        direction = gcmd.get(
            'DIRECTION',
            self.run_direction
        )

        speed = gcmd.get_int(
            'SPEED',
            self.speed
        )

        if target_name:

            target_name = target_name.strip()

        direction = direction.strip().lower()

        if direction not in (
            'back',
            'for'
        ):

            gcmd.respond_error(
                "Ungültige Richtung '%s'. "
                "Erlaubt: back oder for"
                % direction
            )

            return

        if speed < 0 or speed > 255:

            gcmd.respond_error(
                "Ungültige Geschwindigkeit %d."
                % speed
            )

            return

        if duration <= 0:

            gcmd.respond_error(
                "Ungültige Dauer %.2f."
                % duration
            )

            return

        # ----------------------------------------------------
        # ZIEL BESTIMMEN
        # ----------------------------------------------------

        if target_name:

            driver = FILAMENT_DRIVERS.get(
                target_name
            )

            if not driver:

                gcmd.respond_error(
                    "Unbekannte Einheit '%s'. "
                    "Verfügbar: %s"
                    % (
                        target_name,
                        ', '.join(
                            FILAMENT_DRIVERS.keys()
                        )
                    )
                )

                return

            drivers_to_run = [
                driver
            ]

        else:

            drivers_to_run = []

            for name in FILAMENT_ORDER:

                driver = FILAMENT_DRIVERS.get(
                    name
                )

                if driver:

                    drivers_to_run.append(
                        driver
                    )

        # ----------------------------------------------------
        # EINEN NACH DEM ANDEREN
        # ----------------------------------------------------

        for driver in drivers_to_run:

            if driver.is_running:

                gcmd.respond_error(
                    "%s läuft bereits."
                    % driver.name
                )

                return

            gcmd.respond_info(
                "FEED_FILAMENT: %s | "
                "Richtung=%s | "
                "Dauer=%.1fs | "
                "Speed=0x%02X"
                % (
                    driver.name,
                    direction,
                    duration,
                    speed
                )
            )

            if not driver.start_timed_motor(
                direction,
                duration,
                speed,
                gcmd
            ):

                gcmd.respond_error(
                    "Motor %s konnte nicht "
                    "gestartet werden. "
                    "I2C-Bus möglicherweise "
                    "durch %s belegt."
                    % (
                        driver.name,
                        i2c_bus_manager.get_owner()
                    )
                )

                return

            # ------------------------------------------------
            # Wichtig:
            #
            # Die eigentliche Fahrt läuft jetzt
            # asynchron.
            #
            # Deshalb hier NICHT auf das Ende warten.
            # ------------------------------------------------

            return

    # ========================================================
    # EXTRACT BYTES
    # ========================================================

    def _extract_bytes(self, data):

        if isinstance(data, dict):

            if 'response' in data:

                return self._extract_bytes(
                    data['response']
                )

            if 'data' in data:

                return self._extract_bytes(
                    data['data']
                )

            res = []

            for k, val in data.items():

                if k not in (
                    'oid',
                    '#name',
                    'params'
                ):

                    res.extend(
                        self._extract_bytes(val)
                    )

            return res

        if isinstance(
            data,
            (bytes, bytearray)
        ):

            return [
                int(b)
                for b in data
            ]

        if isinstance(
            data,
            (list, tuple)
        ):

            res = []

            for item in data:

                res.extend(
                    self._extract_bytes(item)
                )

            return res

        if isinstance(data, int):

            return [data]

        if isinstance(data, str):

            return [
                ord(c)
                for c in data
            ]

        return []


# ============================================================
# KLIPPER CONFIG
# ============================================================

def load_config_prefix(config):

    return FilamentDriver(config)