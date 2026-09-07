"""Module defining the Flame class with various colours and flicker speeds."""
import random
import time
import math
from dataclasses import dataclass, field

from environment import ENVIRONMENT

@dataclass
class Colour:
    """Dataclass to hold colour settings"""
    name: str | None= None
    hex: int = 0
    p: float = 0.0

    @property
    def rgb(self) -> tuple[int, int, int]:
        colour = self.hex
        r = (colour >> 16) & 0xFF
        g = (colour >> 8) & 0xFF
        b = colour & 0xFF
        return (r, g, b)

@dataclass
class Flicker:
    """Dataclass to hold flicker settings"""
    name: str | None = None
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

CANDLE_FLAME = [Colour(
        getattr(ENVIRONMENT, f'CANDLE_FLAME_COLOUR{i}_NAME'),
        getattr(ENVIRONMENT, f'CANDLE_FLAME_COLOUR{i}_HEX'),
        getattr(ENVIRONMENT, f'CANDLE_FLAME_COLOUR{i}_PROBABILITY')
    ) for i in range(1, 9)]

INFERNAL_FLAME = [
    Colour(
        getattr(ENVIRONMENT, f'INFERNAL_FLAME_COLOUR{i}_NAME'),
        getattr(ENVIRONMENT, f'INFERNAL_FLAME_COLOUR{i}_HEX'),
        getattr(ENVIRONMENT, f'INFERNAL_FLAME_COLOUR{i}_PROBABILITY')
    ) for i in range(1, 9)]

HELLFIRE = [
    Colour(
        getattr(ENVIRONMENT, f'HELLFIRE_COLOUR{i}_NAME'),
        getattr(ENVIRONMENT, f'HELLFIRE_COLOUR{i}_HEX'),
        getattr(ENVIRONMENT, f'HELLFIRE_COLOUR{i}_PROBABILITY')
    ) for i in range(1, 9)]


class Flame:
    """Class representing a flame with various colours and flicker speeds."""

    FLICKER = [
        # Name, probability, min_ms, max_ms, min_brightness, max_brightness
        Flicker(
            "FAST_FLICKER",
            ENVIRONMENT.FAST_FLICKER_PROBABILITY,
            ENVIRONMENT.FAST_FLICKER_MIN_MS,
            ENVIRONMENT.FAST_FLICKER_MAX_MS,
            ENVIRONMENT.FAST_FLICKER_MIN_BRIGHTNESS,
            ENVIRONMENT.FAST_FLICKER_MAX_BRIGHTNESS
        ),
        Flicker(
            "NORMAL_FLICKER",
            ENVIRONMENT.NORMAL_FLICKER_PROBABILITY,
            ENVIRONMENT.NORMAL_FLICKER_MIN_MS,
            ENVIRONMENT.NORMAL_FLICKER_MAX_MS,
            ENVIRONMENT.NORMAL_FLICKER_MIN_BRIGHTNESS,
            ENVIRONMENT.NORMAL_FLICKER_MAX_BRIGHTNESS
        ),
        Flicker(
            "SLOW_FLICKER",
            ENVIRONMENT.SLOW_FLICKER_PROBABILITY,
            ENVIRONMENT.SLOW_FLICKER_MIN_MS,
            ENVIRONMENT.SLOW_FLICKER_MAX_MS,
            ENVIRONMENT.SLOW_FLICKER_MIN_BRIGHTNESS,
            ENVIRONMENT.SLOW_FLICKER_MAX_BRIGHTNESS
        ),
        Flicker(
            "OCC_DIP_FLARE",
            ENVIRONMENT.OCC_DIP_FLARE_PROBABILITY,
            ENVIRONMENT.OCC_DIP_FLARE_MIN_MS,
            ENVIRONMENT.OCC_DIP_FLARE_MAX_MS,
            ENVIRONMENT.OCC_DIP_FLARE_MIN_BRIGHTNESS,
            ENVIRONMENT.OCC_DIP_FLARE_MAX_BRIGHTNESS
        ),
    ]

    GLOBAL_FLICKER = Flicker(
        # Name, probability, min_ms, max_ms, min_brightness, max_brightness
        "GLOBAL_FLICKER",
        ENVIRONMENT.GLOBAL_FLICKER_PROBABILITY,
        ENVIRONMENT.GLOBAL_FLICKER_MIN_MS,
        ENVIRONMENT.GLOBAL_FLICKER_MAX_MS,
        ENVIRONMENT.GLOBAL_FLICKER_MIN_BRIGHTNESS,
        ENVIRONMENT.GLOBAL_FLICKER_MAX_BRIGHTNESS,
    )

    def __init__(self,
                 pixels,
                 led_num: int,
                 change_colour_probability: float = 0.10) -> None:
        self.pixels = pixels
        self.led_num = led_num
        self.change_colour_probability = change_colour_probability

        self.COLOUR_SCHEMES = [
            'CYCLE',
            INFERNAL_FLAME,
            CANDLE_FLAME,
            HELLFIRE,
        ]

        self.ACTIVE_COLOUR_SCHEME = self.COLOUR_SCHEMES[0]
        self.COLOURS = self.ACTIVE_COLOUR_SCHEME

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
            initial_brightness = self._get_target_brightness(
                flicker_type.min_brightness,
                flicker_type.max_brightness
            )
            target_brightness = self._get_target_brightness(
                flicker_type.min_brightness,
                flicker_type.max_brightness
            )
            target_duration = self._get_target_duration(
                flicker_type.min_ms,
                flicker_type.max_ms
            )
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
            r, g, b = led['state'].colour.rgb

            brightness = min(
                led['state'].current_brightness * ENVIRONMENT.LOCAL_FLICKER_WEIGHT
                + self._global_brightness.current_brightness * ENVIRONMENT.GLOBAL_FLICKER_WEIGHT, 1.00
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
                "colour": led["state"].colour,
                "brightness": min(
                    led["state"].current_brightness * ENVIRONMENT.LOCAL_FLICKER_WEIGHT +
                    self._global_brightness.current_brightness * ENVIRONMENT.GLOBAL_FLICKER_WEIGHT, 1.00
                ),
            }
            for led in self.leds
        ]
