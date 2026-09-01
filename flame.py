"""Module defining the Flame class with various colours and flicker speeds."""

import random
import time
import math
from dataclasses import dataclass, field

@dataclass
class Colour:
    """Dataclass to hold colour settings"""
    name: str = None
    hex: int = 0
    p: float = 0.0

@dataclass
class Flicker:
    """Dataclass to hold flicker settings"""
    name: str = None
    p: float = 0.0
    min_ms: int = 0
    max_ms: int = 0
    min_brightness: float = 1.0
    max_brightness: float = 1.0

@dataclass
class State:
    """Dataclass to hold LED States"""
    colour: Colour = field(default_factory=Colour)
    flicker: Flicker = field(default_factory=Flicker)
    current_brightness: float = 1.0
    initial_brightness: float = 1.0
    target_brightness: float = 1.0
    target_duration: int = 0
    started_at: int = 0
    completed_at: int = 0


class Flame:
    """Class representing a flame with various colours and flicker speeds."""

    COLOURS = [
        # Name, hex, probability
        Colour("DEEP_EMBER", 0xDD2800, 0.05),
        Colour("DEEP_ORANGE", 0xFF4500, 0.10),
        Colour("CANDLE_ORANGE", 0xFF6A00, 0.15),
        Colour("AMBER", 0xFF8C00, 0.20),
        Colour("GOLDEN_AMBER", 0xFFA500, 0.20),
        Colour("FLAME_YELLOW", 0xFFC020, 0.15),
        Colour("WARM_YELLOW", 0xFFD35A, 0.10),
        Colour("HOT_FLAME", 0xFFE6A0, 0.05),
    ]

    FLICKER = [
        # Name, probability, min_ms, max_ms, min_brightness, max_brightness
        Flicker("FAST_FLICKER", 0.10, 30, 120, 0.65, 1.00),
        Flicker("NORMAL_FLICKER", 0.55, 120, 400, 0.70, 1.00),
        Flicker("SLOW_FLICKER", 0.30, 500, 2000, 0.75, 1.00),
        Flicker("OCC_DIP_FLARE", 0.05, 50, 250, 0.35, 1.00),
    ]

    GLOBAL_FLICKER = Flicker(
        # Name, probability, min_ms, max_ms, min_brightness, max_brightness
        "GLOBAL_FLICKER",
        1,
        500,
        2000,
        0.75,
        1.00,
    )

    LOCAL_WEIGHT = 0.70
    GLOBAL_WEIGHT = 0.30

    def __init__(self,
                 pixels,
                 led_num: int, 
                 change_colour_probability: float = 0.10) -> None:
        self.pixels = pixels
        self.led_num = led_num
        self.change_colour_probability = change_colour_probability

        initial_global_brightness = self._get_target_brightness(
            self.GLOBAL_FLICKER.min_brightness,
            self.GLOBAL_FLICKER.max_brightness
        )
        target_global_brightness = self._get_target_brightness(
            self.GLOBAL_FLICKER.min_brightness,
            self.GLOBAL_FLICKER.max_brightness
        )
        target_global_duration = self._get_target_duration(
            self.GLOBAL_FLICKER.min_ms,
            self.GLOBAL_FLICKER.max_ms
        )

        now = self._timestamp_ms()
        self._global_brightness = State(
            current_brightness = initial_global_brightness,
            initial_brightness = initial_global_brightness,
            target_brightness = target_global_brightness,
            target_duration = target_global_duration,
            started_at = now,
            completed_at = now + target_global_duration
        )

        self.leds = []

        for led_index in range(led_num):
            flicker_type = self._get_random_flicker()
            initial_brightness = self._get_target_brightness(flicker_type.min_brightness, flicker_type.max_brightness)
            target_brightness = self._get_target_brightness(flicker_type.min_brightness, flicker_type.max_brightness)
            target_duration = self._get_target_duration(flicker_type.min_ms, flicker_type.max_ms)

            now = self._timestamp_ms()
            self.leds.append({
                "name": f"LED_{led_index}",
                "state": State(
                    colour = self._get_random_colour(),
                    flicker = flicker_type,
                    current_brightness = initial_brightness,
                    initial_brightness = initial_brightness,
                    target_brightness = target_brightness,
                    target_duration = target_duration,
                    started_at = now,
                    completed_at = now + target_duration,
                )
            })

    def _get_random_colour(self) -> Colour:
        """Select a random colour based on defined probabilities."""
        return random.choices(
            self.COLOURS,
            weights=[c.p for c in self.COLOURS],
            k=1,
        )[0]

    def _get_random_flicker(self) -> Flicker:
        """Select a random flicker type based on defined probabilities."""
        return random.choices(
            self.FLICKER,
            weights=[f.p for f in self.FLICKER],
            k=1,
        )[0]

    def _get_target_duration(self, min_ms: int, max_ms: int) -> int:
        """Randomly select a target duration from a range"""
        return random.randint(min_ms, max_ms)

    def _get_target_brightness(self, min_brightness: float, max_brightness: float) -> float:
        """Randomly select a target brightness from a range"""
        return random.uniform(min_brightness, max_brightness)
    
    def update(self, test: bool = False) -> None:
        """Update pixels"""
        for led in self.leds:
            led['state'] = self._set_new_state(led['state'])
        self._global_brightness = self._set_new_state(self._global_brightness, global_flicker=True)
        if not test:
            self._update_pixels()

    def _update_pixels(self) -> None:
        """Update the pixels (using Adafruit Neopixels)"""
        for i, led in enumerate(self.leds):
            colour = led['state'].colour.hex
            r = (colour >> 16) & 0xFF
            g = (colour >> 8) & 0xFF
            b = colour & 0xFF

            brightness = min(
                led['state'].current_brightness * self.LOCAL_WEIGHT
                + self._global_brightness.current_brightness * self.GLOBAL_WEIGHT, 1.00
            )

            self.pixels[i] = (
                int(r * brightness),
                int(g * brightness),
                int(b * brightness),
            )
        self.pixels.show()

    def _set_new_state(
        self,
        state: State,
        global_flicker: bool = False
    ) -> State:
        """Set the updated new state"""
        now = self._timestamp_ms()

        if now >= state.completed_at:
            # Complete the previous transition
            state.current_brightness = state.target_brightness

            if global_flicker:
                state.target_brightness = self._get_target_brightness(
                    self.GLOBAL_FLICKER.min_brightness,
                    self.GLOBAL_FLICKER.max_brightness
                )
                state.target_duration = self._get_target_duration(
                    self.GLOBAL_FLICKER.min_ms,
                    self.GLOBAL_FLICKER.max_ms
                )

            else:
                state.flicker = self._get_random_flicker()
                if random.random() < self.change_colour_probability:
                    # The probability of a colour change
                    state.colour = self._get_random_colour()

                state.target_brightness = self._get_target_brightness(
                    state.flicker.min_brightness,
                    state.flicker.max_brightness
                )
                state.target_duration = self._get_target_duration(
                    state.flicker.min_ms,
                    state.flicker.max_ms
                )

            state.initial_brightness = state.current_brightness
            state.started_at = now
            state.completed_at = now + state.target_duration

        else:
            state.current_brightness = self._set_current_brightness(state, now)

        return state

    def _timestamp_ms(self):
        """Return the timestamp in milliseconds"""
        return time.monotonic_ns() // 1_000_000

    def _set_current_brightness(self, state: State, now: int) -> float:
        """Calculate the current brightness."""
        elapsed = now - state.started_at
        progress = min(elapsed / state.target_duration, 1.0)
        smooth = math.sin((math.pi / 2) * progress)

        return (
            state.initial_brightness
            + (state.target_brightness - state.initial_brightness) * smooth
        )

    def get_state(self) -> list:
        """Return a safe snapshot of the current LED state."""
        return [
            {
                "name": led['name'],
                "colour": (led["state"].colour.name, led["state"].colour.hex),
                "brightness": min(led["state"].current_brightness * self.LOCAL_WEIGHT + self._global_brightness.current_brightness * self.GLOBAL_WEIGHT, 1.00),
            }
            for led in self.leds
        ]
