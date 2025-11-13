"""Discord Game Boy Emulator Bot

A Discord bot that runs a Game Boy emulator and allows users to play games
collectively by reacting with emojis to control the game.
"""

__version__ = "0.1.0"
__author__ = "Discord GameBoy Bot"

from discordboy.bot import GameBoyBot
from discordboy.config import Config
from discordboy.controller import InputController
from discordboy.emulator import GameBoyEmulator

__all__ = ["GameBoyBot", "GameBoyEmulator", "InputController", "Config"]
