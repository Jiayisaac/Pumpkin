"""Main application for controlling the Flame LED strip."""
import time
import threading

import board
import neopixel
from adafruit_debouncer import Debouncer
import digitalio

from flame import Flame
from web.main import run_web_server
from environment import ENVIRONMENT

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
    """Handle the button press event to cycle through the flame's colour schemes."""
    flame.ACTIVE_COLOUR_SCHEME = flame.COLOUR_SCHEMES[
        (flame.COLOUR_SCHEMES.index(flame.ACTIVE_COLOUR_SCHEME) + 1) % len(flame.COLOUR_SCHEMES)
        ]
    if not flame.ACTIVE_COLOUR_SCHEME == 'CYCLE':
        flame.COLOURS = flame.ACTIVE_COLOUR_SCHEME


def main():
    """Main loop for updating the Flame LED strip."""
    flame = Flame(pixels, LED_COUNT, CHANGE_COLOUR_PROBABILITY)

    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    cycle_started_at = time.monotonic()
    active_scheme_index = 1

    while True:
        button.update()

        if button.fell:
            on_button_pressed(flame)

            if flame.ACTIVE_COLOUR_SCHEME == "CYCLE":
                active_scheme_index = 1
                flame.COLOURS = flame.COLOUR_SCHEMES[active_scheme_index]
                cycle_started_at = time.monotonic()

        if flame.ACTIVE_COLOUR_SCHEME == "CYCLE":
            if time.monotonic() - cycle_started_at >= 30:
                active_scheme_index += 1
                if active_scheme_index >= len(flame.COLOUR_SCHEMES):
                    active_scheme_index = 1
                flame.COLOURS = flame.COLOUR_SCHEMES[active_scheme_index]
                cycle_started_at = time.monotonic()

        flame.update()
        time.sleep(UPDATE_TIME_SECS)


if __name__ == '__main__':
    main()
