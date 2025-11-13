"""Pytest configuration and shared fixtures."""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest
from pyboy import PyBoy


@pytest.fixture
def mock_rom_path(tmp_path):
    """Create a temporary ROM file path for testing."""
    rom_file = tmp_path / "test_game.gb"
    # Create a minimal valid Game Boy ROM (must be at least 16KB = 0x4000 bytes)
    rom_data = bytearray([0x00] * 0x8000)  # 32KB ROM
    # Add Nintendo logo (required for valid ROM)
    rom_data[0x104:0x134] = [
        0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
        0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
        0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
        0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
        0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
        0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
    ]
    # Add title
    rom_data[0x134:0x143] = b"TEST_GAME\x00\x00\x00\x00\x00\x00"
    # Set cartridge type to 0x00 (ROM ONLY)
    rom_data[0x147] = 0x00
    # Set ROM size to 0x00 (32KB)
    rom_data[0x148] = 0x00

    # Calculate and set header checksum (sum of bytes 0x134-0x14C)
    checksum = 0
    for i in range(0x134, 0x14D):
        checksum = (checksum - rom_data[i] - 1) & 0xFF
    rom_data[0x14D] = checksum

    rom_file.write_bytes(rom_data)
    return rom_file


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    """Mock Config with temporary directories."""
    from discordboy import config

    games_dir = tmp_path / "games"
    saves_dir = tmp_path / "saves"
    games_dir.mkdir()
    saves_dir.mkdir()

    monkeypatch.setattr(config.Config, "GAMES_DIR", games_dir)
    monkeypatch.setattr(config.Config, "SAVES_DIR", saves_dir)
    monkeypatch.setattr(config.Config, "DISCORD_BOT_TOKEN", "test_token_12345")
    monkeypatch.setattr(config.Config, "GAME_CHANNEL_ID", 123456789)
    monkeypatch.setattr(config.Config, "ADMIN_ROLE_ID", 987654321)

    return config.Config


@pytest.fixture
def mock_discord_bot():
    """Create a mock Discord bot for testing."""
    bot = MagicMock()
    bot.user = MagicMock()
    bot.user.name = "TestBot"
    bot.user.id = 123456

    # Mock channel
    channel = MagicMock()
    channel.id = 123456789
    channel.name = "game-channel"
    channel.send = AsyncMock()

    bot.get_channel = MagicMock(return_value=channel)
    bot.start = AsyncMock()
    bot.close = AsyncMock()

    return bot


@pytest.fixture
def mock_discord_message():
    """Create a mock Discord message."""
    message = MagicMock()
    message.id = 999999
    message.channel = MagicMock()
    message.channel.id = 123456789
    message.add_reaction = AsyncMock()
    message.delete = AsyncMock()

    return message


@pytest.fixture
def mock_discord_user():
    """Create a mock Discord user."""
    user = MagicMock()
    user.id = 111111
    user.name = "TestUser"
    user.bot = False
    user.roles = []

    return user


@pytest.fixture
def mock_discord_reaction(mock_discord_message, mock_discord_user):
    """Create a mock Discord reaction."""
    reaction = MagicMock()
    reaction.emoji = "⬆️"
    reaction.message = mock_discord_message

    return reaction


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
