"""PyBoy emulator wrapper for Game Boy emulation."""

from pathlib import Path
from typing import Optional
from PIL import Image
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import logging

logger = logging.getLogger(__name__)


class GameBoyEmulator:
    """Wrapper class for PyBoy emulator."""

    # Mapping of button names to PyBoy WindowEvent
    BUTTON_MAP = {
        "up": (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
        "down": (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
        "left": (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
        "right": (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
        "a": (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
        "b": (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B),
        "start": (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START),
        "select": (WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_SELECT),
    }

    def __init__(self, rom_path: Path, speed: int = 1):
        """Initialize the Game Boy emulator.

        Args:
            rom_path: Path to the ROM file
            speed: Emulation speed multiplier (1 = normal speed)
        """
        if not rom_path.exists():
            raise FileNotFoundError(f"ROM file not found: {rom_path}")

        self.rom_path = rom_path
        self.speed = speed
        self.pyboy: Optional[PyBoy] = None
        self._initialize()

    def _initialize(self):
        """Initialize PyBoy instance."""
        try:
            # Initialize PyBoy in headless mode (no window)
            # Using 'window' instead of deprecated 'window_type'
            self.pyboy = PyBoy(
                str(self.rom_path),
                window="headless",
            )
            self.pyboy.set_emulation_speed(self.speed)
            logger.info(f"Initialized emulator with ROM: {self.rom_path.name}")
        except Exception as e:
            logger.error(f"Failed to initialize emulator: {e}")
            raise

    def tick(self, count: int = 1):
        """Advance emulator by specified number of frames.

        Args:
            count: Number of frames to advance
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        for _ in range(count):
            self.pyboy.tick()

    def press_button(self, button: str):
        """Press a Game Boy button.

        Args:
            button: Button name (up, down, left, right, a, b, start, select)
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        button = button.lower()
        if button not in self.BUTTON_MAP:
            raise ValueError(f"Invalid button: {button}")

        press_event, _ = self.BUTTON_MAP[button]
        self.pyboy.send_input(press_event)
        logger.debug(f"Pressed button: {button}")

    def release_button(self, button: str):
        """Release a Game Boy button.

        Args:
            button: Button name (up, down, left, right, a, b, start, select)
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        button = button.lower()
        if button not in self.BUTTON_MAP:
            raise ValueError(f"Invalid button: {button}")

        _, release_event = self.BUTTON_MAP[button]
        self.pyboy.send_input(release_event)
        logger.debug(f"Released button: {button}")

    def get_screenshot(self) -> Image.Image:
        """Capture current screen as PIL Image.

        Returns:
            PIL Image of the current screen (160x144 pixels)
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        # Get screen buffer from PyBoy
        screen_array = self.pyboy.screen_image()
        return screen_array

    def save_state(self, path: Path):
        """Save emulator state to file.

        Args:
            path: Path to save the state file
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        try:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save state using PyBoy's built-in method
            with open(path, "wb") as f:
                self.pyboy.save_state(f)
            logger.info(f"Saved state to: {path}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise

    def load_state(self, path: Path):
        """Load emulator state from file.

        Args:
            path: Path to the state file
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        if not path.exists():
            raise FileNotFoundError(f"State file not found: {path}")

        try:
            with open(path, "rb") as f:
                self.pyboy.load_state(f)
            logger.info(f"Loaded state from: {path}")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            raise

    def reset(self):
        """Reset the emulator to the beginning of the game."""
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        # Close and reinitialize
        self.close()
        self._initialize()
        logger.info("Emulator reset")

    def set_speed(self, speed: int):
        """Set emulation speed multiplier.

        Args:
            speed: Speed multiplier (1 = normal, higher = faster)
        """
        if not self.pyboy:
            raise RuntimeError("Emulator not initialized")

        self.speed = max(1, min(speed, 10))  # Clamp between 1-10
        self.pyboy.set_emulation_speed(self.speed)
        logger.info(f"Set emulation speed to: {self.speed}x")

    def close(self):
        """Clean up emulator resources."""
        if self.pyboy:
            try:
                self.pyboy.stop()
                logger.info("Emulator stopped")
            except Exception as e:
                logger.error(f"Error stopping emulator: {e}")
            finally:
                self.pyboy = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
