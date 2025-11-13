"""Main Discord bot implementation."""

import asyncio
import logging
import time
from typing import Optional
import discord
from discord.ext import commands
from discordboy.emulator import GameBoyEmulator
from discordboy.controller import InputController
from discordboy.screenshot import capture_screenshot, create_error_image
from discordboy.config import Config
from discordboy.utils import (
    load_rom_list,
    validate_rom,
    is_admin,
    format_game_name,
    create_embed,
    get_save_list,
    format_uptime,
)

logger = logging.getLogger(__name__)


class GameBoyBot(commands.Bot):
    """Discord bot for running Game Boy emulator."""

    def __init__(self):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True

        super().__init__(command_prefix="/", intents=intents)

        self.emulator: Optional[GameBoyEmulator] = None
        self.controller: Optional[InputController] = None
        self.game_channel: Optional[discord.TextChannel] = None
        self.current_message: Optional[discord.Message] = None
        self.game_loop_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.current_rom: Optional[str] = None
        self.start_time: Optional[float] = None
        self.input_count = 0

    async def setup_hook(self):
        """Set up bot commands."""
        logger.info("Bot setup completed")

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Logged in as {self.user.name} ({self.user.id})")

        # Get game channel
        self.game_channel = self.get_channel(Config.GAME_CHANNEL_ID)
        if not self.game_channel:
            logger.error(f"Game channel {Config.GAME_CHANNEL_ID} not found")
            return

        logger.info(f"Using game channel: {self.game_channel.name}")

        # Auto-start with default ROM if available
        if Config.DEFAULT_ROM and validate_rom(Config.DEFAULT_ROM):
            await self._start_game(Config.DEFAULT_ROM)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Handle emoji reactions."""
        # Ignore if not in game channel or game not running
        if not self.is_running or reaction.message.channel.id != Config.GAME_CHANNEL_ID:
            return

        # Only process reactions on the current game message
        if not self.current_message or reaction.message.id != self.current_message.id:
            return

        # Process the input
        emoji = str(reaction.emoji)
        await self.controller.handle_reaction(emoji, user)
        self.input_count += 1

        # Remove reaction for cleaner interface
        try:
            await reaction.remove(user)
        except discord.Forbidden:
            pass
        except Exception as e:
            logger.debug(f"Could not remove reaction: {e}")

    async def _start_game(self, rom_name: str) -> bool:
        """Internal method to start a game.

        Args:
            rom_name: Name of the ROM file

        Returns:
            True if game started successfully
        """
        try:
            if self.is_running:
                await self._stop_game()

            logger.info(f"Starting game: {rom_name}")

            # Initialize emulator
            rom_path = Config.get_rom_path(rom_name)
            self.emulator = GameBoyEmulator(rom_path, Config.GAME_SPEED)

            # Initialize controller with update callback
            self.controller = InputController(self.emulator, self._update_screen)
            await self.controller.start()

            # Start game loop (or just post initial screen if input-driven)
            self.is_running = True
            self.current_rom = rom_name
            self.start_time = time.time()
            self.input_count = 0

            if Config.INPUT_DRIVEN:
                # Just post initial screen, updates happen on input
                await self._update_screen()
            else:
                # Start continuous game loop
                self.game_loop_task = asyncio.create_task(self._game_loop())

            logger.info(f"Game started: {rom_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to start game: {e}")
            await self._send_error(f"Failed to start game: {str(e)}")
            return False

    async def _stop_game(self):
        """Internal method to stop the current game."""
        try:
            logger.info("Stopping game")
            self.is_running = False

            # Stop game loop
            if self.game_loop_task:
                self.game_loop_task.cancel()
                try:
                    await self.game_loop_task
                except asyncio.CancelledError:
                    pass

            # Stop controller
            if self.controller:
                await self.controller.stop()

            # Clean up emulator
            if self.emulator:
                self.emulator.close()

            # Delete current message
            if self.current_message:
                try:
                    await self.current_message.delete()
                except:
                    pass
                self.current_message = None

            self.current_rom = None
            logger.info("Game stopped")

        except Exception as e:
            logger.error(f"Error stopping game: {e}")

    async def _game_loop(self):
        """Main game loop that updates the emulator and posts screenshots."""
        logger.info("Game loop started")

        try:
            while self.is_running:
                # Tick emulator forward
                ticks = int(Config.TICKS_PER_UPDATE * Config.GAME_SPEED)
                self.emulator.tick(ticks)

                # Capture screenshot
                overlay_text = f"{format_game_name(self.current_rom)}"
                screenshot = await capture_screenshot(self.emulator, overlay_text)

                # Post or edit message with new screenshot
                file = discord.File(screenshot, filename="game.png")

                if not self.current_message:
                    # First message - create it
                    self.current_message = await self.game_channel.send(file=file)

                    # Add reaction controls only once
                    for emoji in Config.CONTROL_EMOJIS:
                        try:
                            await self.current_message.add_reaction(emoji)
                        except Exception as e:
                            logger.error(f"Failed to add reaction {emoji}: {e}")
                else:
                    # Update by deleting and reposting (Discord doesn't allow editing attachments)
                    try:
                        await self.current_message.delete()
                    except:
                        pass

                    self.current_message = await self.game_channel.send(file=file)

                    # Re-add reactions (do this in background to avoid blocking)
                    asyncio.create_task(self._add_reactions(self.current_message))

                # Wait for next update
                await asyncio.sleep(Config.UPDATE_INTERVAL)

        except asyncio.CancelledError:
            logger.info("Game loop cancelled")
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            await self._send_error(f"Game loop error: {str(e)}")
            self.is_running = False

    async def _update_screen(self):
        """Update the game screenshot (used in input-driven mode)."""
        try:
            # Tick emulator a few frames
            self.emulator.tick(30)  # Half second of gameplay

            # Capture screenshot
            overlay_text = f"{format_game_name(self.current_rom)}"
            screenshot = await capture_screenshot(self.emulator, overlay_text)

            # Post or update message
            file = discord.File(screenshot, filename="game.png")

            if not self.current_message:
                # First message - create it
                self.current_message = await self.game_channel.send(file=file)

                # Add reaction controls only once
                for emoji in Config.CONTROL_EMOJIS:
                    try:
                        await self.current_message.add_reaction(emoji)
                    except Exception as e:
                        logger.error(f"Failed to add reaction {emoji}: {e}")
            else:
                # Update by deleting and reposting
                try:
                    await self.current_message.delete()
                except:
                    pass

                self.current_message = await self.game_channel.send(file=file)

                # Re-add reactions in background
                asyncio.create_task(self._add_reactions(self.current_message))

        except Exception as e:
            logger.error(f"Error updating screen: {e}")

    async def _add_reactions(self, message: discord.Message):
        """Add control reactions to a message (background task)."""
        for emoji in Config.CONTROL_EMOJIS:
            try:
                await message.add_reaction(emoji)
                await asyncio.sleep(0.25)  # Small delay to avoid rate limits
            except Exception as e:
                logger.debug(f"Failed to add reaction {emoji}: {e}")

    async def _send_error(self, error_message: str):
        """Send an error message to the game channel."""
        try:
            error_image = await create_error_image(error_message)
            file = discord.File(error_image, filename="error.png")
            await self.game_channel.send(file=file)
        except Exception as e:
            logger.error(f"Failed to send error image: {e}")

    # Commands

    @commands.command(name="start")
    async def start_game(self, ctx: commands.Context, rom_name: str = None):
        """Start a game (admin only)."""
        if not is_admin(ctx.author):
            await ctx.send("❌ You need admin permissions to use this command.")
            return

        if not rom_name:
            await ctx.send("❌ Please specify a ROM name. Use `/games` to see available games.")
            return

        if not validate_rom(rom_name):
            await ctx.send(f"❌ ROM not found: {rom_name}")
            return

        success = await self._start_game(rom_name)
        if success:
            embed = create_embed(
                "🎮 Game Started",
                f"Now playing: **{format_game_name(rom_name)}**",
                discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to start game. Check logs for details.")

    @commands.command(name="stop")
    async def stop_game(self, ctx: commands.Context):
        """Stop the current game (admin only)."""
        if not is_admin(ctx.author):
            await ctx.send("❌ You need admin permissions to use this command.")
            return

        if not self.is_running:
            await ctx.send("❌ No game is currently running.")
            return

        await self._stop_game()
        embed = create_embed(
            "🛑 Game Stopped",
            "The game has been stopped.",
            discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(name="speed")
    async def set_speed(self, ctx: commands.Context, speed: int = None):
        """Set emulator speed (admin only)."""
        if not is_admin(ctx.author):
            await ctx.send("❌ You need admin permissions to use this command.")
            return

        if not self.is_running:
            await ctx.send("❌ No game is currently running.")
            return

        if speed is None:
            await ctx.send("❌ Please specify a speed (1-10).")
            return

        if speed < 1 or speed > 10:
            await ctx.send("❌ Speed must be between 1 and 10.")
            return

        self.emulator.set_speed(speed)
        Config.GAME_SPEED = speed

        embed = create_embed(
            "⚡ Speed Changed",
            f"Emulator speed set to **{speed}x**",
            discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="reset")
    async def reset_game(self, ctx: commands.Context):
        """Reset the current game (admin only)."""
        if not is_admin(ctx.author):
            await ctx.send("❌ You need admin permissions to use this command.")
            return

        if not self.is_running:
            await ctx.send("❌ No game is currently running.")
            return

        self.emulator.reset()
        embed = create_embed(
            "🔄 Game Reset",
            "The game has been reset to the beginning.",
            discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command(name="savestate")
    async def savestate(self, ctx: commands.Context, save_name: str = None):
        """Save the current game state (admin only)."""
        if not is_admin(ctx.author):
            await ctx.send("❌ You need admin permissions to use this command.")
            return

        if not self.is_running:
            await ctx.send("❌ No game is currently running.")
            return

        if not save_name:
            save_name = f"{self.current_rom}_{int(time.time())}"

        try:
            save_path = Config.get_save_path(save_name)
            self.emulator.save_state(save_path)

            embed = create_embed(
                "💾 State Saved",
                f"Game state saved as: **{save_name}**",
                discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to save state: {str(e)}")

    @commands.command(name="loadstate")
    async def loadstate(self, ctx: commands.Context, save_name: str = None):
        """Load a saved game state (admin only)."""
        if not is_admin(ctx.author):
            await ctx.send("❌ You need admin permissions to use this command.")
            return

        if not self.is_running:
            await ctx.send("❌ No game is currently running.")
            return

        if not save_name:
            saves = get_save_list()
            if not saves:
                await ctx.send("❌ No save states found.")
                return
            await ctx.send(f"Available saves: {', '.join(saves)}")
            return

        try:
            save_path = Config.get_save_path(save_name)
            self.emulator.load_state(save_path)

            embed = create_embed(
                "📂 State Loaded",
                f"Loaded game state: **{save_name}**",
                discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to load state: {str(e)}")

    @commands.command(name="games")
    async def games(self, ctx: commands.Context):
        """List available games."""
        roms = load_rom_list()

        if not roms:
            await ctx.send("❌ No ROM files found in the games directory.")
            return

        game_list = "\n".join([f"• {format_game_name(rom)} (`{rom}`)" for rom in roms])

        embed = create_embed(
            "🎮 Available Games",
            game_list,
            discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        """Show help information."""
        help_text = """
**How to Play:**
React with emojis on the game screenshot to control the game!

**Controls:**
⬆️ ⬇️ ⬅️ ➡️ - D-pad
🅰️ 🅱️ - A and B buttons
▶️ - Start
⏸️ - Select

**Admin Commands:**
`/start <rom_name>` - Start a game
`/stop` - Stop the current game
`/speed <1-10>` - Set emulator speed
`/reset` - Reset the game
`/savestate <name>` - Save game state
`/loadstate <name>` - Load game state

**Public Commands:**
`/games` - List available games
`/stats` - Show game statistics
`/help` - Show this help message
"""

        embed = create_embed(
            "ℹ️ Game Boy Bot Help",
            help_text,
            discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context):
        """Show current game statistics."""
        if not self.is_running:
            await ctx.send("❌ No game is currently running.")
            return

        uptime = format_uptime(time.time() - self.start_time)
        queue_size = self.controller.get_queue_size()

        fields = [
            ("Game", format_game_name(self.current_rom), True),
            ("Uptime", uptime, True),
            ("Speed", f"{Config.GAME_SPEED}x", True),
            ("Total Inputs", str(self.input_count), True),
            ("Queue Size", str(queue_size), True),
        ]

        embed = create_embed(
            "📊 Game Statistics",
            "",
            discord.Color.blue(),
            fields
        )
        await ctx.send(embed=embed)


async def run_bot():
    """Run the Discord bot."""
    # Validate configuration
    Config.validate()

    # Create and run bot
    bot = GameBoyBot()

    try:
        await bot.start(Config.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if bot.is_running:
            await bot._stop_game()
        await bot.close()
