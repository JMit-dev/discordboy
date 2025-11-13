"""Configuration and constants for the Discord Game Boy bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot configuration from environment variables and constants."""

    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    # Parse GAME_CHANNEL_ID safely
    _channel_id = os.getenv("GAME_CHANNEL_ID", "0")
    try:
        GAME_CHANNEL_ID = int(_channel_id) if _channel_id.isdigit() else 0
    except (ValueError, AttributeError):
        GAME_CHANNEL_ID = 0

    # Parse ADMIN_ROLE_ID safely
    _admin_role = os.getenv("ADMIN_ROLE_ID")
    if _admin_role and _admin_role.isdigit():
        ADMIN_ROLE_ID = int(_admin_role)
    else:
        ADMIN_ROLE_ID = None

    # Game Configuration
    UPDATE_INTERVAL = float(os.getenv("UPDATE_INTERVAL", "2.0"))
    GAME_SPEED = int(os.getenv("GAME_SPEED", "1"))
    DEFAULT_ROM = os.getenv("DEFAULT_ROM", "game.gb")
    INPUT_DRIVEN = os.getenv("INPUT_DRIVEN", "true").lower() == "true"  # Only update on input

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    GAMES_DIR = PROJECT_ROOT / "games"
    SAVES_DIR = PROJECT_ROOT / "saves"

    # Emulator Settings
    SCREEN_SCALE = 3  # Scale Game Boy screen 3x (160x144 -> 480x432)
    TICKS_PER_UPDATE = 60 * 2  # 60 FPS * 2 seconds default

    # Emoji to Button Mappings
    EMOJI_TO_BUTTON = {
        "⬆️": "up",
        "⬇️": "down",
        "⬅️": "left",
        "➡️": "right",
        "🅰️": "a",
        "🅱️": "b",
        "▶️": "start",
        "⏸️": "select",
    }

    CONTROL_EMOJIS = list(EMOJI_TO_BUTTON.keys())

    # Input Settings
    BUTTON_HOLD_DURATION = 0.1  # Seconds to hold a button press
    INPUT_RATE_LIMIT = 0.5  # Minimum seconds between inputs per user

    # Discord Settings
    MAX_MESSAGE_AGE = 300  # Only accept reactions on messages less than 5 minutes old

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
        if not cls.GAME_CHANNEL_ID:
            raise ValueError("GAME_CHANNEL_ID environment variable is required")

        # Create necessary directories
        cls.GAMES_DIR.mkdir(exist_ok=True)
        cls.SAVES_DIR.mkdir(exist_ok=True)

    @classmethod
    def get_rom_path(cls, rom_name: str) -> Path:
        """Get full path to a ROM file."""
        return cls.GAMES_DIR / rom_name

    @classmethod
    def get_save_path(cls, save_name: str) -> Path:
        """Get full path to a save state file."""
        if not save_name.endswith(".state"):
            save_name += ".state"
        return cls.SAVES_DIR / save_name
