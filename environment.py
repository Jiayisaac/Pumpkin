"""Environment variable management for the Pumpkin project."""
import os

from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv('.env')


@dataclass
class Environment:
    """Dataclass to hold environment variables"""
    PIN: str = os.getenv('PIN', 'D17')
    LED_COUNT: int = int(os.getenv('LED_COUNT', '24'))
    CHANGE_COLOUR_PROBABILITY: float = float(os.getenv('CHANGE_COLOUR_PROBABILITY', '0.10'))
    UPDATE_TIME_MS: int = int(os.getenv('UPDATE_TIME_MS', '10'))
    LOCAL_FLICKER_WEIGHT: float = float(os.getenv('LOCAL_FLICKER_WEIGHT', '0.70'))
    GLOBAL_FLICKER_WEIGHT: float = float(os.getenv('GLOBAL_FLICKER_WEIGHT', '0.30'))

ENVIRONMENT = Environment()
