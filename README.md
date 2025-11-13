# Discord Game Boy Bot

A Discord bot that runs a Game Boy emulator and allows users to play games collectively by reacting with emojis to control the game.

## Motivation

Inspired by "Twitch Plays" style interactive gaming, this project brings collaborative Game Boy gameplay to Discord communities. Users can collectively control classic games through emoji reactions, creating a fun and chaotic multiplayer experience.

## Tech/Framework Used

**Built with:**
- Python 3.10+
- discord.py - Discord API wrapper
- PyBoy - Game Boy emulator
- Pillow - Image processing

## Features

- Real-time Game Boy emulation in Discord
- Multiplayer control via emoji reactions
- Save and load game states
- Adjustable emulation speed
- Rate limiting to prevent spam
- Admin commands for game management

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd discordboy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Create configuration
cp .env.example .env
# Edit .env with your Discord bot token and channel ID

# Add ROM files to games/ directory
cp /path/to/your/game.gb games/

# Run the bot
python -m discordboy
```

## How to Use

1. **Create Discord Bot**: Get a bot token from [Discord Developer Portal](https://discord.com/developers/applications)
2. **Configure**: Set `DISCORD_BOT_TOKEN` and `GAME_CHANNEL_ID` in `.env` file
3. **Add ROMs**: Place Game Boy ROM files in the `games/` directory
4. **Run Bot**: Execute `python -m discordboy`
5. **Play**: React with emojis on the game screenshot to control:
   - ⬆️⬇️⬅️➡️ - D-pad
   - 🅰️🅱️ - A and B buttons
   - ▶️⏸️ - Start and Select

### Commands

**Admin commands** (require admin role):
- `/start <rom_name>` - Start a game
- `/stop` - Stop current game
- `/speed <1-10>` - Adjust emulation speed
- `/savestate <name>` - Save game state
- `/loadstate <name>` - Load game state

**Public commands**:
- `/games` - List available games
- `/help` - Show controls
- `/stats` - View game statistics

## Credits

- [PyBoy](https://github.com/Baekalfen/PyBoy) - Game Boy emulator
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- Inspired by "Twitch Plays Pokemon"

## License

GPL-3.0 License
