"""Main application for controlling the Flame LED strip."""
import time
import threading

import board
import neopixel

from flame import Flame
from web.main import run_web_server
from environment import ENVIRONMENT

PIN = getattr(board, ENVIRONMENT.PIN)
LED_COUNT = ENVIRONMENT.LED_COUNT
CHANGE_COLOUR_PROBABILITY = ENVIRONMENT.CHANGE_COLOUR_PROBABILITY
UPDATE_TIME_SECS = ENVIRONMENT.UPDATE_TIME_MS / 1_000

pixels = neopixel.NeoPixel(
    PIN,
    LED_COUNT,
    auto_write=False
)

def main():
    """Main loop for updating the Flame LED strip."""
    flame = Flame(pixels, LED_COUNT, CHANGE_COLOUR_PROBABILITY)

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )
    web_thread.start()
    
    while True:
        flame.update()
        time.sleep(UPDATE_TIME_SECS)

if __name__ == '__main__':
    main()
