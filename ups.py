"""UPS battery monitoring for the Waveshare UPS HAT (C)."""
import smbus


class UPS:
    """Monitor the Waveshare UPS HAT (C) using its INA219."""
    INA219_ADDRESS = 0x43
    REG_CONFIG = 0x00
    REG_SHUNT_VOLTAGE = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05

    # INA219 calibration for the Waveshare board.
    CALIBRATION_VALUE = 4096
    CURRENT_LSB_MA = 0.1
    POWER_LSB_MW = 2.0

    # Approximate single-cell LiPo operating range.
    MIN_BATTERY_VOLTAGE = 3.0
    MAX_BATTERY_VOLTAGE = 4.2

    def __init__(
        self,
        bus_number: int = 1,
        low_battery_percent: float = 10.0,
    ) -> None:
        self.bus = smbus.SMBus(bus_number)
        self.low_battery_percent = low_battery_percent
        self._configure()

    def _write_register(
        self,
        register: int,
        value: int,
    ) -> None:
        """Write a 16-bit value to an INA219 register."""
        self.bus.write_i2c_block_data(
            self.INA219_ADDRESS,
            register,
            [
                (value >> 8) & 0xFF,
                value & 0xFF,
            ],
        )

    def _read_register(
        self,
        register: int,
        signed: bool = False,
    ) -> int:
        """Read a 16-bit INA219 register."""
        data = self.bus.read_i2c_block_data(
            self.INA219_ADDRESS,
            register,
            2,
        )
        value = (data[0] << 8) | data[1]
        if signed and value > 0x7FFF:
            value -= 0x10000
        return value

    def _configure(self) -> None:
        """Configure and calibrate the INA219."""
        # 32 V bus range
        # 320 mV shunt range
        # 12-bit bus and shunt ADC
        # Continuous shunt and bus measurement
        config = 0x399F
        self._write_register(
            self.REG_CONFIG,
            config,
        )
        self._write_register(
            self.REG_CALIBRATION,
            self.CALIBRATION_VALUE,
        )

    @property
    def voltage(self) -> float:
        """Return battery voltage in volts."""
        raw = self._read_register(self.REG_BUS_VOLTAGE)
        # INA219 bus voltage has a 4 mV LSB and is shifted 3 bits.
        return (raw >> 3) * 0.004

    @property
    def current(self) -> float:
        """
        Return current in milliamps.
        Positive = charging.
        Negative = battery supplying the load.
        """
        # Calibration can occasionally reset, so restore it before reading.
        self._write_register(
            self.REG_CALIBRATION,
            self.CALIBRATION_VALUE,
        )
        raw = self._read_register(
            self.REG_CURRENT,
            signed=True,
        )
        return raw * self.CURRENT_LSB_MA

    @property
    def power(self) -> float:
        """Return power in milliwatts."""
        self._write_register(
            self.REG_CALIBRATION,
            self.CALIBRATION_VALUE,
        )
        raw = self._read_register(self.REG_POWER)
        return raw * self.POWER_LSB_MW

    @property
    def percentage(self) -> float:
        """
        Estimate battery percentage from battery voltage.
        This is only an approximation because LiPo voltage does not
        decrease linearly with state of charge.
        """
        voltage = self.voltage
        percentage = (
            (voltage - self.MIN_BATTERY_VOLTAGE)
            / (self.MAX_BATTERY_VOLTAGE - self.MIN_BATTERY_VOLTAGE)
            * 100
        )
        return max(
            0.0,
            min(100.0, percentage),
        )

    @property
    def charging(self) -> bool:
        """Return True when the battery is charging."""
        return self.current > 0

    @property
    def discharging(self) -> bool:
        """Return True when the battery is supplying power."""
        return self.current < 0

    @property
    def low(self) -> bool:
        """Return True when the battery is below the configured threshold."""
        return self.percentage <= self.low_battery_percent

    def get_state(self) -> dict:
        """Return a snapshot of the UPS state."""
        voltage = self.voltage
        current = self.current
        power = self.power
        percentage = (
            (voltage - self.MIN_BATTERY_VOLTAGE)
            / (self.MAX_BATTERY_VOLTAGE - self.MIN_BATTERY_VOLTAGE)
            * 100
        )
        percentage = max(
            0.0,
            min(100.0, percentage),
        )
        return {
            "voltage": voltage,
            "current": current,
            "power": power,
            "percentage": percentage,
            "charging": current > 0,
            "discharging": current < 0,
            "low": percentage <= self.low_battery_percent,
        }

    def close(self) -> None:
        """Close the I2C bus."""
        self.bus.close()
