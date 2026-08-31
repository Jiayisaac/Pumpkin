"""Module defining the Flame class with various colours and flicker speeds."""

import random
import threading


class Flame:
    """Class representing a flame with various colours and flicker speeds."""

    COLOURS = [
        # Name, hex, probability
        ("DEEP_EMBER", 0xDD2800, 0.05),
        ("DEEP_ORANGE", 0xFF4500, 0.10),
        ("CANDLE_ORANGE", 0xFF6A00, 0.15),
        ("AMBER", 0xFF8C00, 0.20),
        ("GOLDEN_AMBER", 0xFFA500, 0.20),
        ("FLAME_YELLOW", 0xFFC020, 0.15),
        ("WARM_YELLOW", 0xFFD35A, 0.10),
        ("HOT_FLAME", 0xFFE6A0, 0.05),
    ]

    FLICKER = [
        # Name, probability, min_ms, max_ms, min_brightness, max_brightness
        ("FAST_FLICKER", 0.10, 30, 120, 0.65, 1.00),
        ("NORMAL_FLICKER", 0.55, 120, 400, 0.70, 1.00),
        ("SLOW_FLICKER", 0.30, 500, 2000, 0.75, 1.00),
        ("OCC_DIP_FLARE", 0.05, 50, 250, 0.35, 1.00),
    ]

    GLOBAL_FLICKER = (
        # min_ms, max_ms, min_brightness, max_brightness
        500,
        2000,
        0.75,
        1.00,
    )

    LOCAL_WEIGHT = 0.70
    GLOBAL_WEIGHT = 0.30

    def __init__(self,
                 led_num: int, 
                 update_time_ms: int = 30, 
                 change_colour_probability: float = 0.10):
        self.led_num = led_num
        self.update_time_ms = update_time_ms
        self.change_colour_probability = change_colour_probability

        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        self._global_brightness = 1.0
        self._global_thread = None

        self.led_state = []

        for led_index in range(led_num):
            self.led_state.append(
                {
                    "name": f"LED_{led_index}",
                    "colour": self._get_random_colour(),
                    "local_brightness": 0.0,
                    "brightness": 0.0,
                    "thread": None,
                }
            )

    def _get_random_colour(self) -> tuple:
        """Select a random colour based on defined probabilities."""
        return random.choices(
            self.COLOURS,
            weights=[c[2] for c in self.COLOURS],
            k=1,
        )[0]

    def _get_random_flicker(self) -> tuple:
        """Select a random flicker type based on defined probabilities."""
        return random.choices(
            self.FLICKER,
            weights=[f[1] for f in self.FLICKER],
            k=1,
        )[0]

    def start(self):
        """Start global and individual LED flicker threads."""
        self._stop_event.clear()

        self._global_thread = threading.Thread(
            target=self._run_global_flame,
            daemon=True,
        )
        self._global_thread.start()

        for led_index in range(self.led_num):
            thread = threading.Thread(
                target=self._run_led,
                args=(led_index,),
                daemon=True,
            )

            self.led_state[led_index]["thread"] = thread
            thread.start()

    def stop(self):
        """Stop all flame threads."""
        self._stop_event.set()

        if self._global_thread is not None:
            self._global_thread.join(timeout=1.0)

        for led in self.led_state:
            thread = led["thread"]

            if thread is not None:
                thread.join(timeout=1.0)

    def _run_global_flame(self):
        """Maintain the slow brightness movement shared by all LEDs."""
        min_duration, max_duration, min_brightness, max_brightness = self.GLOBAL_FLICKER

        current_brightness = random.uniform(
            min_brightness,
            max_brightness,
        )

        while not self._stop_event.is_set():
            duration_ms = random.randint(
                min_duration,
                max_duration,
            )

            target_brightness = random.uniform(
                min_brightness,
                max_brightness,
            )

            start_brightness = current_brightness

            steps = max(
                1,
                duration_ms // self.update_time_ms,
            )

            for step in range(steps):
                if self._stop_event.is_set():
                    return

                progress = (step + 1) / steps

                brightness = (
                    start_brightness + (target_brightness - start_brightness) * progress
                )

                with self._lock:
                    self._global_brightness = brightness

                self._stop_event.wait(self.update_time_ms / 1000)

            current_brightness = target_brightness

    def _run_led(self, led_index: int):
        """Continuously update one LED's flame state."""
        current_brightness = random.uniform(0.7, 1.0)

        while not self._stop_event.is_set():
            flicker = self._get_random_flicker()

            (
                _,
                _,
                min_duration,
                max_duration,
                min_brightness,
                max_brightness,
            ) = flicker

            duration_ms = random.randint(
                min_duration,
                max_duration,
            )

            target_brightness = random.uniform(
                min_brightness,
                max_brightness,
            )

            start_brightness = current_brightness

            steps = max(
                1,
                duration_ms // self.update_time_ms,
            )

            for step in range(steps):
                if self._stop_event.is_set():
                    return

                progress = (step + 1) / steps

                local_brightness = (
                    start_brightness + (target_brightness - start_brightness) * progress
                )

                with self._lock:
                    global_brightness = self._global_brightness

                    brightness = (
                        local_brightness * self.LOCAL_WEIGHT
                        + global_brightness * self.GLOBAL_WEIGHT
                    )

                    self.led_state[led_index]["local_brightness"] = local_brightness
                    self.led_state[led_index]["brightness"] = brightness

                self._stop_event.wait(self.update_time_ms / 1000)

            current_brightness = target_brightness

            if random.random() < self.change_colour_probability:
                with self._lock:
                    self.led_state[led_index]["colour"] = self._get_random_colour()

    def get_state(self) -> list:
        """Return a safe snapshot of the current LED state."""
        with self._lock:
            return [
                {
                    "name": led["name"],
                    "colour": led["colour"],
                    "brightness": led["brightness"],
                }
                for led in self.led_state
            ]
