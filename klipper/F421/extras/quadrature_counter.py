class QuadratureCounter:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.pio = config.getint('pio')
        self.sm = config.getint('sm')
        self.mcu_name = config.get('mcu', 'RP2040')

        # Encoder and zero offset
        self.value = 0
        self.raw_value = 0
        self.zero_offset = 0

        # Map encoder to its Klipper axis
        self.axis = {
            'x_encoder': 'x',
            'y_encoder': 'y'
        }.get(self.name)

                # Encoder direction
        self.direction = {
            'x_encoder': 1,
            'y_encoder': -1
        }.get(self.name, 1)

        # Diagnostic values
        self.pins = 0
        self.pc = 0
        self.rx = 0
        self.ctrl = 0
        self.exec = 0
        self.instr = 0
        self.marker = 0
        self.fdebug = 0
        self.flevel = 0
        self.clkdiv = 0
        self.shiftctrl = 0
        self.pinctrl = 0

        self.mcu = self.printer.lookup_object(
            'mcu ' + self.mcu_name
        )
        self.oid = self.mcu.create_oid()
        self.query_cmd = None

        self.reactor = self.printer.get_reactor()
        self.timer = self.reactor.register_timer(
            self._poll_counter, self.reactor.NEVER
        )

        self.printer.register_event_handler(
            "klippy:connect", self.handle_connect
        )

        # Register homing event
        self.printer.register_event_handler(
            "homing:home_rails_end", self.handle_homing_end
        )

        self.printer.add_object(
            'quadrature_counter ' + self.name, self
        )

        # Register G-code commands only once
        if self.name == 'x_encoder':
            self.gcode = self.printer.lookup_object('gcode')

            self.gcode.register_command(
                'QUERY_QUADRATURE',
                self.cmd_QUERY_QUADRATURE
            )

            self.gcode.register_command(
                'SET_QUADRATURE_ZERO',
                self.cmd_SET_QUADRATURE_ZERO
            )

    def _read_counter(self):
        result = self.query_cmd.send([
            self.oid, self.pio, self.sm
        ])

        count = result['count']

        self.pins = result['pins']
        self.pc = result['pc']
        self.rx = result['rx']
        self.ctrl = result['ctrl']
        self.exec = result['exec']
        self.instr = result['instr']
        self.marker = result['marker']
        self.fdebug = result['fdebug']
        self.flevel = result['flevel']
        self.clkdiv = result['clkdiv']
        self.shiftctrl = result['shiftctrl']
        self.pinctrl = result['pinctrl']

        # Convert unsigned 32-bit value to signed value
        if count >= 0x80000000:
            count -= 0x100000000

        self.raw_value = count

        # Calculate position relative to zero offset
        relative = (count - self.zero_offset) & 0xffffffff

        if relative >= 0x80000000:
            relative -= 0x100000000

        self.value = relative * self.direction

        return count

        return count

    def set_zero(self):
        # Get a fresh value directly from the RP2040
        current = self._read_counter()

        self.zero_offset = current
        self.value = 0

    def handle_homing_end(self, homing_state, rails):
        if self.axis is None:
            return

        # Identify the rail that has just completed homing
        for rail in rails:
            rail_name = rail.get_name()

            if rail_name == 'stepper_' + self.axis:
                self.set_zero()

                self.printer.lookup_object('gcode').respond_info(
                    "%s encoder: zero set after homing"
                    % self.axis.upper()
                )
                break

    def cmd_SET_QUADRATURE_ZERO(self, gcmd):
        name = gcmd.get('NAME')

        counters = self.printer.lookup_objects(
            'quadrature_counter'
        )

        for object_name, counter in counters:
            if counter.name == name:
                counter.set_zero()
                gcmd.respond_info(
                    "%s encoder zero set" % name
                )
                return

        raise gcmd.error(
            "Unknown quadrature encoder: %s" % name
        )

    def cmd_QUERY_QUADRATURE(self, gcmd):
        counters = self.printer.lookup_objects(
            'quadrature_counter'
        )

        for name, counter in counters:
            gcmd.respond_info(
                "%s: count=%d raw=%d zero=%d GPIO_AB=%d "
                "PC=%d RX=%d CTRL=%08x EXEC=%08x "
                "INSTR=%08x MARKER=%d FDEBUG=%08x "
                "FLEVEL=%08x CLKDIV=%08x SHIFTCTRL=%08x "
                "PINCTRL=%08x"
                % (
                    counter.name,
                    counter.value,
                    counter.raw_value,
                    counter.zero_offset,
                    counter.pins,
                    counter.pc,
                    counter.rx,
                    counter.ctrl,
                    counter.exec,
                    counter.instr,
                    counter.marker,
                    counter.fdebug,
                    counter.flevel,
                    counter.clkdiv,
                    counter.shiftctrl,
                    counter.pinctrl
                )
            )

    def handle_connect(self):
        self.query_cmd = self.mcu.lookup_query_command(
            "get_counter oid=%c pio=%u sm=%u",
            "counter_val oid=%c count=%u pins=%u pc=%u "
            "rx=%u ctrl=%u exec=%u instr=%u marker=%u "
            "fdebug=%u flevel=%u clkdiv=%u "
            "shiftctrl=%u pinctrl=%u",
            oid=self.oid
        )

        self.reactor.update_timer(
            self.timer, self.reactor.monotonic()
        )

    def _poll_counter(self, eventtime):
        self._read_counter()
        return eventtime + 0.1

    def get_status(self, eventtime):
        return {
            'value': self.value,
            'raw_value': self.raw_value,
            'zero_offset': self.zero_offset
        }


def load_config_prefix(config):
    return QuadratureCounter(config)