"""Helper utility functions for the Discord Game Boy bot."""

import logging
from pathlib import Path
from typing import List, Optional
import discord
from discordboy.config import Config

logger = logging.getLogger(__name__)


def load_rom_list() -> List[str]:
    """Scan games directory for available ROM files.

    Returns:
        List of ROM filenames
    """
    try:
        if not Config.GAMES_DIR.exists():
            logger.warning(f"Games directory not found: {Config.GAMES_DIR}")
            return []

        # Find all .gb and .gbc files
        roms = []
        for extension in ["*.gb", "*.gbc"]:
            roms.extend(Config.GAMES_DIR.glob(extension))

        # Return just the filenames
        rom_names = [rom.name for rom in roms]
        rom_names.sort()

        logger.info(f"Found {len(rom_names)} ROM(s)")
        return rom_names

    except Exception as e:
        logger.error(f"Error loading ROM list: {e}")
        return []


def validate_rom(rom_name: str) -> bool:
    """Check if a ROM file is valid and exists.

    Args:
        rom_name: Name of the ROM file

    Returns:
        True if ROM is valid, False otherwise
    """
    try:
        rom_path = Config.get_rom_path(rom_name)

        if not rom_path.exists():
            logger.warning(f"ROM file not found: {rom_name}")
            return False

        if rom_path.suffix.lower() not in [".gb", ".gbc"]:
            logger.warning(f"Invalid ROM file extension: {rom_name}")
            return False

        # Check file is not empty
        if rom_path.stat().st_size == 0:
            logger.warning(f"ROM file is empty: {rom_name}")
            return False

        return True

    except Exception as e:
        logger.error(f"Error validating ROM {rom_name}: {e}")
        return False


def is_admin(member: discord.Member) -> bool:
    """Check if a user has admin permissions.

    Args:
        member: Discord member to check

    Returns:
        True if user is admin, False otherwise
    """
    try:
        # Check for administrator permission
        if member.guild_permissions.administrator:
            return True

        # Check for configured admin role
        if Config.ADMIN_ROLE_ID:
            admin_role = discord.utils.get(member.roles, id=Config.ADMIN_ROLE_ID)
            if admin_role:
                return True

        return False

    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


def format_game_name(filename: str) -> str:
    """Clean up ROM filename for display.

    Args:
        filename: ROM filename

    Returns:
        Formatted game name
    """
    try:
        # Remove extension
        name = Path(filename).stem

        # Replace underscores and hyphens with spaces
        name = name.replace("_", " ").replace("-", " ")

        # Title case
        name = name.title()

        return name

    except Exception as e:
        logger.error(f"Error formatting game name: {e}")
        return filename


def create_embed(
    title: str,
    description: str,
    color: discord.Color = discord.Color.blue(),
    fields: Optional[List[tuple]] = None
) -> discord.Embed:
    """Create a Discord embed message.

    Args:
        title: Embed title
        description: Embed description
        color: Embed color
        fields: Optional list of (name, value, inline) tuples

    Returns:
        Discord Embed object
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    if fields:
        for field_name, field_value, inline in fields:
            embed.add_field(name=field_name, value=field_value, inline=inline)

    return embed


def get_save_list() -> List[str]:
    """Get list of available save state files.

    Returns:
        List of save state filenames
    """
    try:
        if not Config.SAVES_DIR.exists():
            return []

        saves = list(Config.SAVES_DIR.glob("*.state"))
        save_names = [save.stem for save in saves]  # Remove .state extension
        save_names.sort()

        return save_names

    except Exception as e:
        logger.error(f"Error loading save list: {e}")
        return []


def format_uptime(seconds: float) -> str:
    """Format uptime in seconds to human-readable string.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted uptime string (e.g., "2h 34m 12s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def setup_logging(level: int = logging.INFO):
    """Set up logging configuration.

    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
