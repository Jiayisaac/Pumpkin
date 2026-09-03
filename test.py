"""Visual test application for the Flame class."""
import tkinter as tk

from environment import ENVIRONMENT
from flame import Flame

LED_COUNT = ENVIRONMENT.LED_COUNT
BOX_SIZE = 50
BOX_GAP = 10
COLUMNS = 5
WINDOW_BACKGROUND = "#202020"
UPDATE_TIME_MS = ENVIRONMENT.UPDATE_TIME_MS


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

        self.root.after(
            UPDATE_TIME_MS,
            self._update,
        )

    def _update(self):
        """Update the flame state and display."""

        self.flame.update(test=True)
        self._update_display()

        self.root.after(
            UPDATE_TIME_MS,
            self._update,
        )

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
        colour: tuple[int, int, int],
        brightness: float,
    ) -> str:
        """Apply brightness to a 24-bit RGB colour."""

        r, g, b = colour

        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _update_display(self):
        """Update LED boxes from the current flame state."""

        state = self.flame.get_state()

        for led_index, led in enumerate(state):
            colour = led["colour"]

            colour_name = colour.name
            colour_value = colour.rgb
            brightness = led["brightness"]

            display_colour = self._apply_brightness(
                colour_value,
                brightness,
            )

            self.canvas.itemconfigure(
                self.rectangles[led_index],
                fill=display_colour,
            )

            self.canvas.itemconfigure(
                self.labels[led_index],
                text=(f"{led_index}: {colour_name}\n" f"{brightness:.2f}"),
            )

    def _on_close(self):
        """Close the application."""
        self.root.destroy()


def main():
    """Run the Flame test application."""

    root = tk.Tk()
    FlameTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
