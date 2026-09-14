"""Main application for controlling the Flame LED strip."""
import time
import threading

import board
import neopixel
from adafruit_debouncer import Debouncer
import digitalio

from flame import (
    CANDLE_FLAME,
    COLOUR_SCHEMES,
    HELLFIRE,
    INFERNAL_FLAME,
    Flame,
)
from web.main import run_web_server
from environment import ENVIRONMENT
from wifi import WiFi

LED_PIN = getattr(board, ENVIRONMENT.LED_PIN)
BUTTON_PIN = getattr(board, ENVIRONMENT.BUTTON_PIN)
LED_COUNT = ENVIRONMENT.LED_COUNT
CHANGE_COLOUR_PROBABILITY = ENVIRONMENT.CHANGE_COLOUR_PROBABILITY
UPDATE_TIME_SECS = ENVIRONMENT.UPDATE_TIME_MS / 1_000

pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    auto_write=False
)

pin = digitalio.DigitalInOut(BUTTON_PIN)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
button = Debouncer(pin)


def on_button_pressed(flame: Flame):
    """Handle a button press by cycling through the available colour schemes."""
    current_index = COLOUR_SCHEMES.index(flame.active_colour_scheme)
    next_index = (current_index + 1) % len(COLOUR_SCHEMES)
    flame.set_colour_scheme(COLOUR_SCHEMES[next_index])


def main():
    """Main loop for updating the Flame LED strip."""
    flame = Flame(pixels, LED_COUNT, CHANGE_COLOUR_PROBABILITY)

    wifi_thread = threading.Thread(
        target=WiFi.service,
        daemon=True
    )
    wifi_thread.start()

    web_thread = threading.Thread(
        target=run_web_server,
        args=(flame,),
        daemon=True
    )
    web_thread.start()

    cycle_started_at = time.monotonic()
    active_scheme_index = 1
    previous_colour_scheme = flame.active_colour_scheme

    while True:
        button.update()

        if button.fell:
            on_button_pressed(flame)

        if flame.active_colour_scheme != previous_colour_scheme:
            if flame.active_colour_scheme == 'CYCLE':
                active_scheme_index = 1
                flame.set_colour_scheme('CYCLE')
                cycle_started_at = time.monotonic()

            previous_colour_scheme = flame.active_colour_scheme

        if flame.active_colour_scheme == 'CYCLE':
            if time.monotonic() - cycle_started_at >= 30:
                active_scheme_index += 1

                if active_scheme_index >= len(COLOUR_SCHEMES):
                    active_scheme_index = 1

                scheme = COLOUR_SCHEMES[active_scheme_index]
                flame.colours = {
                    'INFERNAL_FLAME': INFERNAL_FLAME,
                    'CANDLE_FLAME': CANDLE_FLAME,
                    'HELLFIRE': HELLFIRE,
                }[scheme]
                cycle_started_at = time.monotonic()

        flame.update()
        time.sleep(UPDATE_TIME_SECS)


if __name__ == '__main__':
    main()
