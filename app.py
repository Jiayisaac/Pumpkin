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
    flame.COLOURS = flame.ACTIVE_COLOUR_SCHEME


def main():
    """Main loop for updating the Flame LED strip."""
    flame = Flame(pixels, LED_COUNT, CHANGE_COLOUR_PROBABILITY)

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )
    web_thread.start()

    while True:
        button.update()
        if button.fell:
            on_button_pressed(flame)
        flame.update()
        time.sleep(UPDATE_TIME_SECS)


if __name__ == '__main__':
    main()
