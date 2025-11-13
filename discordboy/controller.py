"""Input controller for mapping emoji reactions to Game Boy controls."""

import asyncio
import time
import logging
from typing import Dict, Optional
import discord
from discordboy.emulator import GameBoyEmulator
from discordboy.config import Config

logger = logging.getLogger(__name__)


class InputController:
    """Handles input processing from Discord reactions to Game Boy controls."""

    def __init__(self, emulator: GameBoyEmulator):
        """Initialize the input controller.

        Args:
            emulator: GameBoyEmulator instance to send inputs to
        """
        self.emulator = emulator
        self.input_queue: asyncio.Queue = asyncio.Queue()
        self.user_last_input: Dict[int, float] = {}  # Track rate limiting per user
        self.processing_task: Optional[asyncio.Task] = None
        self.is_running = False

    async def start(self):
        """Start the input processing task."""
        if self.is_running:
            logger.warning("Input controller already running")
            return

        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_queue())
        logger.info("Input controller started")

    async def stop(self):
        """Stop the input processing task."""
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        logger.info("Input controller stopped")

    async def handle_reaction(self, emoji: str, user: discord.User):
        """Handle an emoji reaction from a user.

        Args:
            emoji: The emoji string
            user: Discord user who reacted
        """
        # Ignore bot reactions
        if user.bot:
            return

        # Check if emoji is a valid control
        if emoji not in Config.EMOJI_TO_BUTTON:
            logger.debug(f"Invalid emoji: {emoji}")
            return

        # Rate limiting per user
        current_time = time.time()
        user_id = user.id

        if user_id in self.user_last_input:
            time_since_last = current_time - self.user_last_input[user_id]
            if time_since_last < Config.INPUT_RATE_LIMIT:
                logger.debug(f"Rate limited user {user.name}")
                return

        # Update last input time and queue the input
        self.user_last_input[user_id] = current_time
        await self.input_queue.put((emoji, user))
        logger.debug(f"Queued input {emoji} from {user.name}")

    async def _process_queue(self):
        """Process inputs from the queue (runs in background task)."""
        logger.info("Started input queue processor")

        while self.is_running:
            try:
                # Wait for next input with timeout
                emoji, user = await asyncio.wait_for(
                    self.input_queue.get(), timeout=1.0
                )
                await self._process_input(emoji, user)
            except asyncio.TimeoutError:
                # No input received, continue loop
                continue
            except asyncio.CancelledError:
                logger.info("Input processor cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing input: {e}")
                await asyncio.sleep(0.1)

    async def _process_input(self, emoji: str, user: discord.User):
        """Process a single input.

        Args:
            emoji: The emoji to process
            user: User who sent the input
        """
        try:
            # Map emoji to button
            button = Config.EMOJI_TO_BUTTON.get(emoji)
            if not button:
                return

            # Press button
            self.emulator.press_button(button)
            logger.info(f"{user.name} pressed {button}")

            # Hold for configured duration
            await asyncio.sleep(Config.BUTTON_HOLD_DURATION)

            # Release button
            self.emulator.release_button(button)

            # Small delay between inputs
            await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"Error processing input {emoji}: {e}")

    def clear_rate_limits(self):
        """Clear rate limiting data (useful for testing or reset)."""
        self.user_last_input.clear()
        logger.info("Cleared rate limit data")

    def get_queue_size(self) -> int:
        """Get current input queue size.

        Returns:
            Number of inputs waiting in queue
        """
        return self.input_queue.qsize()
