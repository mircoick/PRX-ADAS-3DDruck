import logging
import time
from . import bus
from . import i2c_bus_manager
from collections import deque


class STM32TempSensor:

    def __init__(self, config, reg_addr=0x04):

        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]

        self.reg_addr = reg_addr

        self.temp = 20.0
        self.temp_samples = deque(maxlen=10)

        self.min_temp = 0.0
        self.max_temp = 200.0

        self.sample_cb = None

        # ----------------------------------------------------
        # I2C
        # ----------------------------------------------------

        self.i2c_addr = config.getint(
            'i2c_addr',
            0x6A
        )

        self.i2c = bus.MCU_I2C_from_config(
            config,
            default_addr=self.i2c_addr,
            default_speed=100000
        )

        # ----------------------------------------------------
        # REACTOR
        # ----------------------------------------------------

        self.reactor = self.printer.get_reactor()

        self.printer.register_event_handler(
            "klippy:connect",
            self._handle_connect
        )

        # ----------------------------------------------------
        # GCODE
        # ----------------------------------------------------

        gcode = self.printer.lookup_object(
            'gcode'
        )

        try:

            gcode.register_command(
                "SET_FAN_PWM",
                self.cmd_SET_FAN_PWM,
                desc="Setzt PWM in Reg 0x05"
            )

        except Exception:
            pass

    # ========================================================
    # CONNECT
    # ========================================================

    def _handle_connect(self):

        self.reactor.register_timer(
            self._sample_sensor_timer,
            self.reactor.monotonic() + 1.0
        )

    # ========================================================
    # TEMPERATUR TIMER
    # ========================================================

    def _sample_sensor_timer(self, eventtime):

        # I2C-Bus wird anderweitig verwendet
        if i2c_bus_manager.is_busy():

            logging.debug(
                "Temperatur %s: "
                "I2C-Bus momentan durch %s belegt.",
                self.name,
                i2c_bus_manager.get_owner()
            )

            return eventtime + 1.0

        try:

            raw = self.i2c.i2c_read(
                [self.reg_addr],
                1
            )

            if isinstance(raw, dict) and 'response' in raw:
                raw = raw['response']

            if isinstance(raw, (bytes, bytearray)) and len(raw) > 0:

                # Aktuelle Rohmessung
                measured_temp = float(raw[0])

                # Messung zum gleitenden Mittelwert hinzufügen
                self.temp_samples.append(measured_temp)

                # Mittelwert aller verfügbaren Messungen berechnen
                self.temp = (
                    sum(self.temp_samples)
                    / len(self.temp_samples)
                )

                # Temperatur an Klipper weitergeben
                if self.sample_cb:
                    self.sample_cb(
                        eventtime,
                        self.temp
                    )

                logging.debug(
                    "Temperatur %s: Rohwert=%.2f, "
                    "Mittelwert=%.2f, Messungen=%d",
                    self.name,
                    measured_temp,
                    self.temp,
                    len(self.temp_samples)
                )

        except Exception as e:

            logging.debug(
                "Fehler beim Abrufen der Temperatur "
                "(Reg 0x%02X): %s",
                self.reg_addr,
                str(e)
            )

        return eventtime + 1.0

    # ========================================================
    # MIN / MAX
    # ========================================================

    def setup_minmax(
        self,
        min_temp,
        max_temp
    ):

        self.min_temp = min_temp
        self.max_temp = max_temp

    # ========================================================
    # CALLBACK
    # ========================================================

    def setup_callback(self, cb):

        self.sample_cb = cb

    # ========================================================
    # GET TEMP
    # ========================================================

    def get_temp(self, eventtime):

        return self.temp, 0.0

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self, eventtime):

        return {
            'temperature': round(
                self.temp,
                2
            )
        }

    # ========================================================
    # READ REG
    # ========================================================

    def read_stm32_reg(
        self,
        reg,
        length=1
    ):

        self.i2c.i2c_write(
            [reg]
        )

        time.sleep(0.002)

        return self.i2c.i2c_read(
            [],
            length
        )

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

    # ========================================================
    # FAN PWM
    # ========================================================

    def cmd_SET_FAN_PWM(
        self,
        gcmd
    ):

        pwm_val = gcmd.get_int(
            'VALUE',
            80,
            minval=0,
            maxval=160
        )

        reg = 0x05

        # ----------------------------------------------------
        # Bus reservieren
        # ----------------------------------------------------

        if not i2c_bus_manager.acquire(
            self.name
        ):

            gcmd.respond_error(
                "I2C-Bus momentan durch %s belegt."
                % i2c_bus_manager.get_owner()
            )

            return

        try:

            self.i2c.i2c_write(
                [reg, pwm_val]
            )

            time.sleep(
                0.002
            )

            raw_data = self.read_stm32_reg(
                reg,
                1
            )

            byte_list = self._extract_bytes(
                raw_data
            )

            if byte_list:

                gcmd.respond_info(
                    "PWM %d (0x%02X) gesetzt. "
                    "Antwort-Wert aus Reg 0x05: "
                    "%d (0x%02X)"
                    % (
                        pwm_val,
                        pwm_val,
                        byte_list[0],
                        byte_list[0]
                    )
                )

            else:

                gcmd.respond_info(
                    "Keine Antwort vom "
                    "Unterboard empfangen."
                )

        except Exception as e:

            gcmd.respond_error(
                "Fehler bei PWM-Steuerung: %s"
                % str(e)
            )

        finally:

            i2c_bus_manager.release(
                self.name
            )


# ============================================================
# SENSOR 2
# ============================================================

class STM32TempSensor2(
    STM32TempSensor
):

    def __init__(self, config):

        super().__init__(
            config,
            reg_addr=0x0E
        )


# ============================================================
# KLIPPER
# ============================================================

def load_config(config):

    pheaters = (
        config.get_printer()
        .load_object(
            config,
            'heaters'
        )
    )

    pheaters.add_sensor_factory(
        'stm32_temp',
        STM32TempSensor
    )

    pheaters.add_sensor_factory(
        'stm32_temp2',
        STM32TempSensor2
    )