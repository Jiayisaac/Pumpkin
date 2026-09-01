"""Main application for controlling the Flame LED strip."""
import time

import board
import neopixel

from flame import Flame

PIN = board.D17
LED_NUM = 20

pixels = neopixel.NeoPixel(
    PIN,
    LED_NUM,
    auto_write=False
)

def main():
    """Main loop for updating the Flame LED strip."""
    flame = Flame(pixels, LED_NUM)
    while True:
        flame.update()
        time.sleep(0.01)

if __name__ == '__main__':
    main()
