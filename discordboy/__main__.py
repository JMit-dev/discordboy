"""Main entry point for the Discord Game Boy bot."""

import asyncio
import sys

from discordboy.bot import run_bot
from discordboy.utils import setup_logging


def main():
    """Main entry point."""
    # Setup logging
    setup_logging()

    # Run the bot
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
