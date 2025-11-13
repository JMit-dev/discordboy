"""Tests for emulator module."""

import pytest
from PIL import Image
from discordboy.emulator import GameBoyEmulator


def test_emulator_init(mock_rom_path):
    """Test emulator initialization."""
    emulator = GameBoyEmulator(mock_rom_path, speed=1)
    assert emulator.rom_path == mock_rom_path
    assert emulator.speed == 1
    assert emulator.pyboy is not None
    emulator.close()


def test_emulator_init_invalid_rom(tmp_path):
    """Test emulator fails with invalid ROM path."""
    invalid_rom = tmp_path / "nonexistent.gb"
    with pytest.raises(FileNotFoundError):
        GameBoyEmulator(invalid_rom)


def test_emulator_tick(mock_rom_path):
    """Test emulator tick advancement."""
    emulator = GameBoyEmulator(mock_rom_path)
    try:
        emulator.tick(10)  # Should not raise
    finally:
        emulator.close()


def test_emulator_press_button(mock_rom_path):
    """Test button press."""
    emulator = GameBoyEmulator(mock_rom_path)
    try:
        emulator.press_button("a")
        emulator.press_button("UP")  # Test case insensitive
    finally:
        emulator.close()


def test_emulator_release_button(mock_rom_path):
    """Test button release."""
    emulator = GameBoyEmulator(mock_rom_path)
    try:
        emulator.press_button("b")
        emulator.release_button("b")
    finally:
        emulator.close()


def test_emulator_invalid_button(mock_rom_path):
    """Test pressing invalid button raises error."""
    emulator = GameBoyEmulator(mock_rom_path)
    try:
        with pytest.raises(ValueError, match="Invalid button"):
            emulator.press_button("invalid")
    finally:
        emulator.close()


def test_emulator_get_screenshot(mock_rom_path):
    """Test screenshot capture."""
    emulator = GameBoyEmulator(mock_rom_path)
    try:
        screenshot = emulator.get_screenshot()
        assert isinstance(screenshot, Image.Image)
        assert screenshot.size == (160, 144)  # Game Boy screen size
    finally:
        emulator.close()


def test_emulator_set_speed(mock_rom_path):
    """Test setting emulation speed."""
    emulator = GameBoyEmulator(mock_rom_path, speed=1)
    try:
        emulator.set_speed(5)
        assert emulator.speed == 5

        # Test clamping
        emulator.set_speed(20)
        assert emulator.speed == 10

        emulator.set_speed(0)
        assert emulator.speed == 1
    finally:
        emulator.close()


def test_emulator_save_state(mock_rom_path, tmp_path):
    """Test saving emulator state."""
    emulator = GameBoyEmulator(mock_rom_path)
    save_path = tmp_path / "test_save.state"

    try:
        emulator.tick(100)  # Advance some frames
        emulator.save_state(save_path)
        assert save_path.exists()
        assert save_path.stat().st_size > 0
    finally:
        emulator.close()


def test_emulator_load_state(mock_rom_path, tmp_path):
    """Test loading emulator state."""
    emulator = GameBoyEmulator(mock_rom_path)
    save_path = tmp_path / "test_save.state"

    try:
        # Save state
        emulator.tick(100)
        emulator.save_state(save_path)

        # Load state
        emulator.load_state(save_path)
    finally:
        emulator.close()


def test_emulator_load_nonexistent_state(mock_rom_path, tmp_path):
    """Test loading nonexistent state file raises error."""
    emulator = GameBoyEmulator(mock_rom_path)
    invalid_path = tmp_path / "nonexistent.state"

    try:
        with pytest.raises(FileNotFoundError):
            emulator.load_state(invalid_path)
    finally:
        emulator.close()


def test_emulator_reset(mock_rom_path):
    """Test emulator reset."""
    emulator = GameBoyEmulator(mock_rom_path)
    try:
        emulator.tick(100)
        emulator.reset()
        # After reset, emulator should still work
        emulator.tick(10)
    finally:
        emulator.close()


def test_emulator_context_manager(mock_rom_path):
    """Test emulator as context manager."""
    with GameBoyEmulator(mock_rom_path) as emulator:
        assert emulator.pyboy is not None
        emulator.tick(10)

    # After exiting context, should be closed
    assert emulator.pyboy is None


def test_button_map_completeness():
    """Test that BUTTON_MAP has all required buttons."""
    from discordboy.emulator import GameBoyEmulator

    required_buttons = ["up", "down", "left", "right", "a", "b", "start", "select"]
    for button in required_buttons:
        assert button in GameBoyEmulator.BUTTON_MAP
        press_event, release_event = GameBoyEmulator.BUTTON_MAP[button]
        assert press_event is not None
        assert release_event is not None
