# Discord Game Boy Bot

A Discord bot that runs a Game Boy emulator and allows users to play games collectively by reacting with emojis to control the game.

## Features

- **Real-time Game Boy Emulation**: Powered by PyBoy for accurate emulation
- **Multiplayer Control**: Multiple users can control the game via emoji reactions
- **Save States**: Save and load game progress at any time
- **Adjustable Speed**: Control emulation speed from 1x to 10x
- **Rate Limiting**: Prevents spam and ensures fair gameplay
- **Admin Commands**: Full control over game management
- **Input-Driven Mode**: Perfect for turn-based games like Pokemon

## Quick Start

```bash
# Install
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your Discord bot token

# Add ROM files
cp your_game.gb games/

# Run
python -m discordboy
```

## Controls

React with these emojis to control the game:

- ⬆️⬇️⬅️➡️ - D-pad movement
- 🅰️🅱️ - A and B buttons
- ▶️ - Start button
- ⏸️ - Select button

## Commands

### Admin Commands
- `/start <rom_name>` - Start a game
- `/stop` - Stop current game
- `/speed <1-10>` - Adjust emulation speed
- `/reset` - Reset the game
- `/savestate <name>` - Save game state
- `/loadstate <name>` - Load game state

### Public Commands
- `/games` - List available games
- `/stats` - View game statistics
- `/help` - Show help message

## Requirements

- Python 3.10+
- Discord.py 2.4.0+
- PyBoy 2.4.1+
- Pillow 11.0.0+

## License

GPL-3.0 License
