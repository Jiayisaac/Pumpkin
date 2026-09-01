"""Visual test application for the Flame class."""

import tkinter as tk
import time

from flame import Flame

LED_COUNT = 20

BOX_SIZE = 50
BOX_GAP = 10
COLUMNS = 5

WINDOW_BACKGROUND = "#202020"

UPDATE_TIME_MS = 30


class FlameTestApp:
    """Visual test application for the Flame class."""

    def __init__(self, root: tk.Tk):
        self.root = root

        self.root.title("Flame LED Test")
        self.root.configure(bg=WINDOW_BACKGROUND)

        self.flame = Flame(
            None,
            led_num=LED_COUNT,
        )

        self.canvas = tk.Canvas(
            root,
            bg=WINDOW_BACKGROUND,
            highlightthickness=0,
        )
        self.canvas.pack(
            padx=20,
            pady=20,
        )

        self.rectangles = []
        self.labels = []

        self._create_led_boxes()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self._on_close,
        )

        while True:
            self.flame.update(test=True)
            self._update_display()
            time.sleep(0.01)

    def _create_led_boxes(self):
        """Create graphical boxes representing each LED."""

        rows = (LED_COUNT + COLUMNS - 1) // COLUMNS

        width = COLUMNS * BOX_SIZE + (COLUMNS - 1) * BOX_GAP

        height = rows * (BOX_SIZE + 25) + (rows - 1) * BOX_GAP

        self.canvas.config(
            width=width,
            height=height,
        )

        for led_index in range(LED_COUNT):
            row = led_index // COLUMNS
            column = led_index % COLUMNS

            x1 = column * (BOX_SIZE + BOX_GAP)
            y1 = row * (BOX_SIZE + BOX_GAP + 25)

            x2 = x1 + BOX_SIZE
            y2 = y1 + BOX_SIZE

            rectangle = self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#000000",
                outline="#606060",
                width=1,
            )

            label = self.canvas.create_text(
                x1 + BOX_SIZE / 2,
                y2 + 12,
                text=f"LED {led_index}",
                fill="#cccccc",
                font=("Arial", 8),
            )

            self.rectangles.append(rectangle)
            self.labels.append(label)

    @staticmethod
    def _apply_brightness(
        colour: int,
        brightness: float,
    ) -> str:
        """
        Apply brightness to a 24-bit RGB colour and
        return a tkinter-compatible hexadecimal colour.
        """

        red = (colour >> 16) & 0xFF
        green = (colour >> 8) & 0xFF
        blue = colour & 0xFF

        red = int(red * brightness)
        green = int(green * brightness)
        blue = int(blue * brightness)

        return f"#{red:02x}" f"{green:02x}" f"{blue:02x}"

    def _update_display(self):
        """Update LED boxes from the current flame state."""

        state = self.flame.get_state()

        for led_index, led in enumerate(state):
            colour_tuple = led["colour"]

            colour_name = colour_tuple[0]
            colour = colour_tuple[1]

            brightness = led["brightness"]

            display_colour = self._apply_brightness(
                colour,
                brightness,
            )

            self.canvas.itemconfigure(
                self.rectangles[led_index],
                fill=display_colour,
            )

            self.canvas.itemconfigure(
                self.labels[led_index],
                text=(f"{led_index}: " f"{colour_name}\n" f"{brightness:.2f}"),
            )

        self.root.after(
            UPDATE_TIME_MS,
            self._update_display,
        )

    def _on_close(self):
        """Stop the Flame instance and close the application."""

        self.flame.stop()
        self.root.destroy()


def main():
    root = tk.Tk()

    FlameTestApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
