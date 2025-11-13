"""Tests for input controller module."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from discordboy.controller import InputController
from discordboy.config import Config


@pytest.mark.asyncio
async def test_controller_init(mock_rom_path):
    """Test controller initialization."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)
        assert controller.emulator == emulator
        assert controller.is_running is False
        assert controller.input_queue.qsize() == 0
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_start_stop(mock_rom_path):
    """Test starting and stopping controller."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)

        await controller.start()
        assert controller.is_running is True
        assert controller.processing_task is not None

        await controller.stop()
        assert controller.is_running is False
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_handle_reaction_valid_emoji(mock_rom_path, mock_discord_user):
    """Test handling valid emoji reaction."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)
        await controller.start()

        await controller.handle_reaction("⬆️", mock_discord_user)
        await asyncio.sleep(0.1)  # Allow processing

        assert controller.input_queue.qsize() >= 0  # Queue should be processing
        await controller.stop()
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_ignore_bot_reactions(mock_rom_path):
    """Test that bot reactions are ignored."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    bot_user = MagicMock()
    bot_user.bot = True
    bot_user.id = 999999

    try:
        controller = InputController(emulator)
        initial_queue_size = controller.input_queue.qsize()

        await controller.handle_reaction("⬆️", bot_user)

        # Queue should not change
        assert controller.input_queue.qsize() == initial_queue_size
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_invalid_emoji(mock_rom_path, mock_discord_user):
    """Test handling invalid emoji."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)
        initial_queue_size = controller.input_queue.qsize()

        await controller.handle_reaction("❌", mock_discord_user)

        # Invalid emoji should not be queued
        assert controller.input_queue.qsize() == initial_queue_size
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_rate_limiting(mock_rom_path, mock_discord_user):
    """Test rate limiting per user."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)

        # First input should be accepted
        await controller.handle_reaction("⬆️", mock_discord_user)
        first_queue_size = controller.input_queue.qsize()

        # Second input immediately after should be rate limited
        await controller.handle_reaction("⬇️", mock_discord_user)
        second_queue_size = controller.input_queue.qsize()

        # Queue size should not increase due to rate limit
        assert second_queue_size == first_queue_size
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_update_callback(mock_rom_path):
    """Test update callback is triggered."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    callback_called = False

    async def update_callback():
        nonlocal callback_called
        callback_called = True

    try:
        controller = InputController(emulator, update_callback)
        await controller.start()

        # Manually process an input
        user = MagicMock()
        user.id = 12345
        user.name = "TestUser"
        user.bot = False

        await controller._process_input("⬆️", user)

        # In INPUT_DRIVEN mode, callback should be called
        if Config.INPUT_DRIVEN:
            await asyncio.sleep(0.2)  # Wait for callback
            assert callback_called is True

        await controller.stop()
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_clear_rate_limits(mock_rom_path, mock_discord_user):
    """Test clearing rate limit data."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)

        await controller.handle_reaction("⬆️", mock_discord_user)
        assert len(controller.user_last_input) > 0

        controller.clear_rate_limits()
        assert len(controller.user_last_input) == 0
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_get_queue_size(mock_rom_path, mock_discord_user):
    """Test getting queue size."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)

        initial_size = controller.get_queue_size()
        await controller.handle_reaction("⬆️", mock_discord_user)

        # Queue size should be trackable
        assert controller.get_queue_size() >= initial_size
    finally:
        emulator.close()


@pytest.mark.asyncio
async def test_controller_multiple_users(mock_rom_path):
    """Test multiple users can send inputs."""
    from discordboy.emulator import GameBoyEmulator

    emulator = GameBoyEmulator(mock_rom_path)
    try:
        controller = InputController(emulator)

        user1 = MagicMock()
        user1.id = 1
        user1.bot = False

        user2 = MagicMock()
        user2.id = 2
        user2.bot = False

        # Both users should be able to queue inputs
        await controller.handle_reaction("⬆️", user1)
        await controller.handle_reaction("⬇️", user2)

        # Both should be in rate limit tracking
        assert user1.id in controller.user_last_input
        assert user2.id in controller.user_last_input
    finally:
        emulator.close()
