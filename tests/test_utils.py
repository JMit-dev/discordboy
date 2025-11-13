"""Tests for utils module."""

import pytest
from unittest.mock import MagicMock
from discordboy.utils import (
    format_game_name,
    format_uptime,
    is_admin,
    create_embed,
)


def test_format_game_name():
    """Test formatting game names."""
    assert format_game_name("pokemon_red.gb") == "Pokemon Red"
    assert format_game_name("super_mario_land.gb") == "Super Mario Land"
    assert format_game_name("zelda.gb") == "Zelda"
    assert format_game_name("GAME.GB") == "Game"


def test_format_game_name_with_version():
    """Test formatting game names with version numbers."""
    name = format_game_name("pokemon_red_v1.2.gb")
    assert "Pokemon" in name
    assert "Red" in name


def test_format_uptime_seconds():
    """Test formatting uptime in seconds."""
    assert format_uptime(30) == "30s"
    assert format_uptime(59) == "59s"


def test_format_uptime_minutes():
    """Test formatting uptime in minutes."""
    assert format_uptime(60) == "1m"
    assert format_uptime(125) == "2m 5s"
    assert format_uptime(3599) == "59m 59s"


def test_format_uptime_hours():
    """Test formatting uptime in hours."""
    assert format_uptime(3600) == "1h"
    assert format_uptime(7265) == "2h 1m 5s"


def test_format_uptime_days():
    """Test formatting uptime in days."""
    # Note: The function doesn't handle days separately, so 24h shows as hours
    assert format_uptime(86400) == "24h"
    assert format_uptime(90000) == "25h"


def test_is_admin_with_role(mock_config):
    """Test admin check with correct role."""
    user = MagicMock()
    role = MagicMock()
    role.id = mock_config.ADMIN_ROLE_ID
    user.roles = [role]

    assert is_admin(user) is True


def test_is_admin_without_role():
    """Test admin check without admin role."""
    from discordboy.config import Config

    user = MagicMock()
    user.guild_permissions.administrator = False  # Not an admin
    role = MagicMock()
    role.id = 999999  # Different role ID (not matching Config.ADMIN_ROLE_ID)
    user.roles = [role]

    assert is_admin(user) is False


def test_is_admin_no_role_configured(monkeypatch):
    """Test admin check when no admin role is configured."""
    from discordboy import config

    monkeypatch.setattr(config.Config, "ADMIN_ROLE_ID", None)

    user = MagicMock()
    user.roles = []

    # When no admin role is set, everyone should be admin
    assert is_admin(user) is True


def test_is_admin_multiple_roles(mock_config):
    """Test admin check with multiple roles."""
    user = MagicMock()

    role1 = MagicMock()
    role1.id = 111111

    role2 = MagicMock()
    role2.id = mock_config.ADMIN_ROLE_ID

    role3 = MagicMock()
    role3.id = 333333

    user.roles = [role1, role2, role3]

    assert is_admin(user) is True


def test_create_embed_basic():
    """Test creating basic embed."""
    embed = create_embed("Test Title", "Test Description")

    assert embed.title == "Test Title"
    assert embed.description == "Test Description"


def test_create_embed_with_color():
    """Test creating embed with color."""
    import discord

    embed = create_embed("Title", "Description", discord.Color.blue())
    assert embed.color == discord.Color.blue()


def test_create_embed_with_fields():
    """Test creating embed with fields."""
    fields = [
        ("Field 1", "Value 1", True),
        ("Field 2", "Value 2", False),
    ]

    embed = create_embed("Title", "Description", fields=fields)

    assert len(embed.fields) == 2
    assert embed.fields[0].name == "Field 1"
    assert embed.fields[0].value == "Value 1"
    assert embed.fields[0].inline is True


def test_create_embed_no_fields():
    """Test creating embed without fields."""
    embed = create_embed("Title", "Description")
    assert len(embed.fields) == 0
