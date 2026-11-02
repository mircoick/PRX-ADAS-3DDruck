
#include <stdint.h>

#include "hardware/structs/pio.h"
#include "hardware/structs/io_bank0.h"
#include "hardware/structs/sio.h"
#include "hardware/structs/pads_bank0.h"
#include "hardware/structs/resets.h"

#include "command.h"
#include "sched.h"

/*
 * RP2040 quadrature decoder
 *
 * Based on the official Raspberry Pi quadrature_encoder PIO example.
 *
 * PIO0:
 *   SM0: GPIO 2 (A), GPIO 3 (B)
 *   SM1: GPIO 4 (A), GPIO 5 (B)
 *
 * Both state machines share one PIO program.
 * The program occupies addresses 0..23.
 */

#define PIO_PROGRAM_LENGTH 24
#define PIO_WRAP_BOTTOM    15
#define PIO_WRAP_TOP       23

#define GPIO_FUNC_PIO0     6

#define PIO_SM_ENABLE(sm)  (1u << (sm))
#define PIO_RX_EMPTY(sm)   (1u << (8 + (sm)))

#define RESET_PIO0 (1u << 10)

static void
quadrature_release_pio0(void)
{
    /* Release PIO0 from reset. */
    resets_hw->reset &= ~RESET_PIO0;

    /* Wait until PIO0 is operational. */
    while (!(resets_hw->reset_done & RESET_PIO0))
        ;
}

static const uint16_t quadrature_program[PIO_PROGRAM_LENGTH] = {
    0x000f, 0x000e, 0x0015, 0x000f,
    0x0015, 0x000f, 0x000f, 0x000e,
    0x000e, 0x000f, 0x000f, 0x0015,
    0x000f, 0x0015, 0x008f, 0xa0c2,
    0x8000, 0x60c2, 0x4002, 0xa0e6,
    0xa0a6, 0xa04a, 0x0097, 0xa04a
};

static volatile uint32_t quadrature_init_marker = 0;

/* Load the PIO program once into PIO0 instruction memory. */
static void
quadrature_load_program(void)
{
    int i;

    for (i = 0; i < PIO_PROGRAM_LENGTH; i++)
        pio0_hw->instr_mem[i] = quadrature_program[i];
}

/* Initialize one quadrature encoder state machine. */
static void
quadrature_init_sm(uint32_t sm, uint32_t pin)
{
    pio_hw_t *pio = pio0_hw;
    pio_sm_hw_t *state = &pio->sm[sm];

    uint32_t pin_state;
    uint32_t initial_position;

    /* Keep the state machine disabled during configuration. */
    pio->ctrl &= ~PIO_SM_ENABLE(sm);

    /* Assign both GPIOs to PIO0. */
    io_bank0_hw->io[pin].ctrl =
        (io_bank0_hw->io[pin].ctrl & ~0x1fu) | GPIO_FUNC_PIO0;

    io_bank0_hw->io[pin + 1].ctrl =
        (io_bank0_hw->io[pin + 1].ctrl & ~0x1fu) | GPIO_FUNC_PIO0;

    /* Enable input and internal pull-up on both encoder pins. */
    pads_bank0_hw->io[pin] &= ~(1u << 2);
    pads_bank0_hw->io[pin + 1] &= ~(1u << 2);

    pads_bank0_hw->io[pin] |= (1u << 6) | (1u << 3);
    pads_bank0_hw->io[pin + 1] |= (1u << 6) | (1u << 3);

    /* Read the initial A/B state after configuring the pads. */
    pin_state = (sio_hw->gpio_in >> pin) & 3u;
    /*
     * Position mapping used by the Raspberry Pi reference decoder.
     */
    switch (pin_state) {
    case 0:
        initial_position = 0;
        break;
    case 1:
        initial_position = 3;
        break;
    case 2:
        initial_position = 1;
        break;
    default:
        initial_position = 2;
        break;
    }

    /* PIO clock divider = 1 (full system clock). */
    state->clkdiv = 1u << 16;

    /* Program loop wraps from instruction 23 back to 15. */
    state->execctrl =
        (PIO_WRAP_TOP << 12) |
        (PIO_WRAP_BOTTOM << 7);

    /* OUT shifts right; IN shifts left; no automatic FIFO shifting. */
    state->shiftctrl = 1u << 19;

    /* IN PINS starts at the encoder's A pin. */
    state->pinctrl = pin << 15;

    /*
     * Initialize OSR with the inverted previous pin state.
     * Then initialize Y with the corresponding quadrature position.
     */
    state->instr = 0xe040u | ((~pin_state) & 0x1fu);
    state->instr = 0xa0e2u;  /* MOV OSR, Y */
    state->instr = 0xe040u | (initial_position & 0x1fu);

    /* Start execution at instruction 15 (update). */
    state->instr = PIO_WRAP_BOTTOM;

    /* Enable this state machine. */
    pio->ctrl |= PIO_SM_ENABLE(sm);
}

/* Initialize both encoders. */
void
counter_init(void)
{
    quadrature_init_marker = 1;

    /* PIO0 must be released before accessing its registers. */
    quadrature_release_pio0();

    quadrature_load_program();

    quadrature_init_sm(0, 2);
    quadrature_init_sm(1, 4);

    /* Clear FIFO debug flags for both state machines. */
    pio0_hw->fdebug = (1u << 0) | (1u << 1);

    quadrature_init_marker = 2;
}

DECL_INIT(counter_init);

static int32_t
quadrature_get_count(uint32_t sm)
{
    pio_hw_t *pio = pio0_hw;
    uint32_t count = 0;
    uint32_t fstat = pio->fstat;
    uint32_t rx_empty = 1u << (sm + 8);

    for (uint32_t i = 0; i < 4; i++) {
        if (fstat & rx_empty)
            break;

        count = pio->rxf[sm];
        fstat = pio->fstat;
    }

    return (int32_t)count;
}

/* Klipper command: get_counter pio=0 sm=0 */
void
command_get_counter(uint32_t *args)
{
    uint8_t oid = args[0];
    uint32_t pio = args[1];
    uint32_t sm = args[2];

    uint32_t pin;
    uint32_t pins;
    uint32_t pc;
    uint32_t rx_level;
    uint32_t ctrl;
    uint32_t execctrl;
    uint32_t instr;
    uint32_t fdebug;
    uint32_t flevel;
    uint32_t sm_clkdiv;
    uint32_t sm_shiftctrl;
    uint32_t sm_pinctrl;

    int32_t count;
    uint32_t marker = quadrature_init_marker;

    if (pio != 0 || sm > 1) {
        sendf(
            "counter_val oid=%c count=%u pins=%u pc=%u rx=%u "
            "ctrl=%u exec=%u instr=%u marker=%u "
            "fdebug=%u flevel=%u clkdiv=%u shiftctrl=%u pinctrl=%u",
            oid, 0u, 0u, 0u, 0u,
            0u, 0u, 0u, 0u,
            0u, 0u, 0u, 0u, 0u);
        return;
    }

    ctrl = pio0_hw->ctrl;
    execctrl = pio0_hw->sm[sm].execctrl;
    instr = pio0_hw->sm[sm].instr;
    pc = pio0_hw->sm[sm].addr & 0x1f;

    rx_level = (pio0_hw->flevel >> (sm * 8 + 4)) & 0x0f;

    pin = (sm == 0) ? 2 : 4;
    pins = (sio_hw->gpio_in >> pin) & 3u;

    count = quadrature_get_count(sm);

    fdebug = pio0_hw->fdebug;
    flevel = pio0_hw->flevel;
    sm_clkdiv = pio0_hw->sm[sm].clkdiv;
    sm_shiftctrl = pio0_hw->sm[sm].shiftctrl;
    sm_pinctrl = pio0_hw->sm[sm].pinctrl;

    sendf(
        "counter_val oid=%c count=%u pins=%u pc=%u rx=%u "
        "ctrl=%u exec=%u instr=%u marker=%u "
        "fdebug=%u flevel=%u clkdiv=%u shiftctrl=%u pinctrl=%u",
        oid, (uint32_t)count, pins, pc, rx_level,
        ctrl, execctrl, instr, marker,
        fdebug, flevel, sm_clkdiv, sm_shiftctrl, sm_pinctrl);
}

DECL_COMMAND(command_get_counter,
    "get_counter oid=%c pio=%u sm=%u");
