"""Tests for configuration module."""

import os
from pathlib import Path

import pytest
from discordboy.config import Config


def test_config_has_required_attributes():
    """Test that Config has all required attributes."""
    assert hasattr(Config, "DISCORD_BOT_TOKEN")
    assert hasattr(Config, "GAME_CHANNEL_ID")
    assert hasattr(Config, "ADMIN_ROLE_ID")
    assert hasattr(Config, "GAMES_DIR")
    assert hasattr(Config, "SAVES_DIR")
    assert hasattr(Config, "EMOJI_TO_BUTTON")
    assert hasattr(Config, "CONTROL_EMOJIS")


def test_emoji_to_button_mapping():
    """Test emoji to button mapping is correct."""
    assert Config.EMOJI_TO_BUTTON["⬆️"] == "up"
    assert Config.EMOJI_TO_BUTTON["⬇️"] == "down"
    assert Config.EMOJI_TO_BUTTON["⬅️"] == "left"
    assert Config.EMOJI_TO_BUTTON["➡️"] == "right"
    assert Config.EMOJI_TO_BUTTON["🅰️"] == "a"
    assert Config.EMOJI_TO_BUTTON["🅱️"] == "b"
    assert Config.EMOJI_TO_BUTTON["▶️"] == "start"
    assert Config.EMOJI_TO_BUTTON["⏸️"] == "select"


def test_control_emojis_list():
    """Test control emojis list matches mapping keys."""
    assert len(Config.CONTROL_EMOJIS) == 8
    assert set(Config.CONTROL_EMOJIS) == set(Config.EMOJI_TO_BUTTON.keys())


def test_get_rom_path(mock_config):
    """Test getting ROM file path."""
    rom_path = mock_config.get_rom_path("test.gb")
    assert rom_path == mock_config.GAMES_DIR / "test.gb"
    assert isinstance(rom_path, Path)


def test_get_save_path(mock_config):
    """Test getting save state path."""
    save_path = mock_config.get_save_path("test_save")
    assert save_path == mock_config.SAVES_DIR / "test_save.state"
    assert str(save_path).endswith(".state")


def test_get_save_path_with_extension(mock_config):
    """Test getting save state path when extension already provided."""
    save_path = mock_config.get_save_path("test_save.state")
    assert save_path == mock_config.SAVES_DIR / "test_save.state"
    assert str(save_path).count(".state") == 1


def test_config_validate_success(mock_config):
    """Test config validation passes with valid values."""
    try:
        mock_config.validate()
    except ValueError:
        pytest.fail("validate() raised ValueError unexpectedly")


def test_config_validate_missing_token(monkeypatch):
    """Test config validation fails without bot token."""
    from discordboy import config

    monkeypatch.setattr(config.Config, "DISCORD_BOT_TOKEN", None)
    with pytest.raises(ValueError, match="DISCORD_BOT_TOKEN"):
        config.Config.validate()


def test_config_validate_missing_channel(monkeypatch):
    """Test config validation fails without channel ID."""
    from discordboy import config

    monkeypatch.setattr(config.Config, "DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setattr(config.Config, "GAME_CHANNEL_ID", 0)
    with pytest.raises(ValueError, match="GAME_CHANNEL_ID"):
        config.Config.validate()


def test_screen_scale_setting():
    """Test screen scale configuration."""
    assert Config.SCREEN_SCALE == 3
    assert isinstance(Config.SCREEN_SCALE, int)


def test_ticks_per_update_setting():
    """Test ticks per update configuration."""
    assert Config.TICKS_PER_UPDATE == 120  # 60 FPS * 2 seconds
    assert isinstance(Config.TICKS_PER_UPDATE, int)
