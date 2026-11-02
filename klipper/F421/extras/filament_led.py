import logging

from . import bus
from . import i2c_bus_manager


LED_DEVICES = {
    "Support_4": 0x6C,
    "Model_2":   0x6D,
    "Support_3": 0x6E,
    "Model_1":   0x6F,
}


# ============================================================
# GLOBALE LED-OBJEKTE
# ============================================================

FILAMENT_LEDS = {}


class FilamentLED:

    def __init__(self, config):

        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]

        if self.name not in LED_DEVICES:
            raise config.error(
                "Unbekanntes LED-Modul '%s'. Erlaubt: %s"
                % (
                    self.name,
                    ', '.join(LED_DEVICES.keys())
                )
            )

        self.i2c_addr = config.getint(
            'i2c_addr',
            LED_DEVICES[self.name]
        )

        self.i2c = bus.MCU_I2C_from_config(
            config,
            default_addr=self.i2c_addr,
            default_speed=10000
        )

        self.reactor = self.printer.get_reactor()

        # ----------------------------------------------------
        # Dieses konkrete Objekt registrieren
        # ----------------------------------------------------

        FILAMENT_LEDS[self.name] = self

        logging.info(
            "FilamentLED geladen: %s -> I2C 0x%02X",
            self.name,
            self.i2c_addr
        )


    # ========================================================
    # I2C
    # ========================================================

    def write_reg(self, reg, value):

        try:

            self.i2c.i2c_write([
                reg,
                value
            ])

            return True

        except Exception as e:

            logging.debug(
                "LED I2C Write Fehler "
                "(%s / 0x%02X) "
                "Reg 0x%02X = 0x%02X: %s",
                self.name,
                self.i2c_addr,
                reg,
                value,
                str(e)
            )

            return False


    # ========================================================
    # BUS
    # ========================================================

    def acquire_bus(self):

        return i2c_bus_manager.acquire(
            "LED_" + self.name
        )


    def release_bus(self):

        i2c_bus_manager.release(
            "LED_" + self.name
        )


    # ========================================================
    # RGB
    # ========================================================

    def set_rgb(
        self,
        red,
        green,
        blue
    ):

        red = max(
            0,
            min(255, int(red))
        )

        green = max(
            0,
            min(255, int(green))
        )

        blue = max(
            0,
            min(255, int(blue))
        )

        if not self.acquire_bus():
            return False

        try:

            if not self.write_reg(
                0x60,
                red
            ):
                return False

            if not self.write_reg(
                0x61,
                green
            ):
                return False

            if not self.write_reg(
                0x62,
                blue
            ):
                return False

            return True

        finally:

            self.release_bus()


    # ========================================================
    # BLINK
    # ========================================================

    def set_blink(
        self,
        speed
    ):

        speed = max(
            0,
            min(255, int(speed))
        )

        if not self.acquire_bus():
            return False

        try:

            return self.write_reg(
                0x63,
                speed
            )

        finally:

            self.release_bus()


    # ========================================================
    # NFC
    # ========================================================

    def update_nfc(self):

        if not self.acquire_bus():
            return False

        try:

            return self.write_reg(
                0x0B,
                0x01
            )

        finally:

            self.release_bus()


# ============================================================
# NAME -> LED
# ============================================================

def get_led(gcmd):

    name = gcmd.get(
        'NAME',
        None
    )

    if not name:

        raise gcmd.error(
            "NAME muss angegeben werden. "
            "Verfügbar: %s"
            % ', '.join(LED_DEVICES.keys())
        )

    name = name.strip()

    led = FILAMENT_LEDS.get(name)

    if led is None:

        raise gcmd.error(
            "LED '%s' wurde nicht gefunden. "
            "Geladen: %s"
            % (
                name,
                ', '.join(FILAMENT_LEDS.keys())
            )
        )

    return led


# ============================================================
# SET FILAMENT LED
# ============================================================

def cmd_SET_FILAMENT_LED(gcmd):

    led = get_led(gcmd)

    red = gcmd.get_int(
        'R',
        0,
        minval=0,
        maxval=255
    )

    green = gcmd.get_int(
        'G',
        0,
        minval=0,
        maxval=255
    )

    blue = gcmd.get_int(
        'B',
        0,
        minval=0,
        maxval=255
    )

    logging.info(
        "SET_FILAMENT_LED: NAME=%s -> I2C 0x%02X",
        led.name,
        led.i2c_addr
    )

    if not led.set_rgb(
        red,
        green,
        blue
    ):

        gcmd.respond_error(
            "%s: I2C-Bus momentan belegt "
            "oder LED konnte nicht geschrieben werden."
            % led.name
        )

        return

    gcmd.respond_info(
        "%s: LED RGB gesetzt auf "
        "R=%d G=%d B=%d "
        "(I2C 0x%02X)"
        % (
            led.name,
            red,
            green,
            blue,
            led.i2c_addr
        )
    )


# ============================================================
# SET BLINK
# ============================================================

def cmd_SET_FILAMENT_LED_BLINK(gcmd):

    led = get_led(gcmd)

    speed = gcmd.get_int(
        'SPEED',
        0,
        minval=0,
        maxval=255
    )

    if not led.set_blink(
        speed
    ):

        gcmd.respond_error(
            "%s: Blinkgeschwindigkeit "
            "konnte nicht gesetzt werden."
            % led.name
        )

        return

    gcmd.respond_info(
        "%s: LED-Blinkgeschwindigkeit "
        "auf 0x%02X gesetzt "
        "(I2C 0x%02X)."
        % (
            led.name,
            speed,
            led.i2c_addr
        )
    )


# ============================================================
# NFC UPDATE
# ============================================================

def cmd_UPDATE_FILAMENT_NFC(gcmd):

    led = get_led(gcmd)

    if not led.update_nfc():

        gcmd.respond_error(
            "%s: NFC-Aktualisierung konnte "
            "nicht gestartet werden."
            % led.name
        )

        return

    gcmd.respond_info(
        "%s: NFC-Aktualisierung gestartet "
        "(I2C 0x%02X)."
        % (
            led.name,
            led.i2c_addr
        )
    )


# ============================================================
# KLIPPER CONFIG
# ============================================================

def load_config_prefix(config):

    printer = config.get_printer()
    gcode = printer.lookup_object('gcode')

    # --------------------------------------------------------
    # G-Codes nur einmal registrieren
    # --------------------------------------------------------

    if not hasattr(printer, '_filament_led_gcode_registered'):

        gcode.register_command(
            "SET_FILAMENT_LED",
            cmd_SET_FILAMENT_LED,
            desc="Setzt die RGB-LED eines Filament-Moduls"
        )

        gcode.register_command(
            "SET_FILAMENT_LED_BLINK",
            cmd_SET_FILAMENT_LED_BLINK,
            desc="Setzt die Blinkgeschwindigkeit der Filament-LED"
        )

        gcode.register_command(
            "UPDATE_FILAMENT_NFC",
            cmd_UPDATE_FILAMENT_NFC,
            desc="Startet eine NFC-Aktualisierung"
        )

        printer._filament_led_gcode_registered = True

    return FilamentLED(config)