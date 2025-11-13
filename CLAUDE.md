# Discord Game Boy Emulator Bot

## Project Overview
A Discord bot that runs a Game Boy emulator (PyBoy) and allows users to play games collectively by reacting with emojis to control the game. The bot takes screenshots of the game and posts them to Discord, where users can react with directional and button emojis to send inputs to the emulator. Please make atomic commits for every feature with a tag like feat: chore: docs: fix: etc... and make sure it has a one sentence after it and do not credit yourself.

## Core Features
1. Run PyBoy emulator in the bot process
2. Capture game screenshots at regular intervals
3. Post screenshots to a designated Discord channel
4. Listen for emoji reactions on game screenshots
5. Map emoji reactions to Game Boy controls (D-pad, A, B, Start, Select)
6. Update game state based on user inputs
7. Support multiple games that can be loaded/switched
8. Admin commands to control the bot (start game, stop game, change game, set speed)

## Technical Stack
- **Language**: Python 3.10+
- **Discord Library**: discord.py 2.0+
- **Emulator**: PyBoy
- **Image Processing**: Pillow (PIL)
- **Environment Variables**: python-dotenv
- **Async**: asyncio

## Project Structure
```
discord-gameboy-bot/
├── bot.py                 # Main bot entry point
├── emulator.py           # PyBoy emulator wrapper
├── controller.py         # Input mapping and control logic
├── screenshot.py         # Screenshot capture and processing
├── config.py             # Configuration and constants
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
└── games/               # Directory for ROM files (gitignored)
    └── .gitkeep
```

## Dependencies (requirements.txt)

PLEASE USE THE LATEST VERSIONS

```
discord.py>=2.0.0
pyboy>=1.6.0
Pillow>=10.0.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
```

## Environment Variables (.env)
```
DISCORD_BOT_TOKEN=your_bot_token_here
GAME_CHANNEL_ID=your_channel_id_here
ADMIN_ROLE_ID=your_admin_role_id_here (optional)
UPDATE_INTERVAL=2.0
GAME_SPEED=1
DEFAULT_ROM=game.gb
```

## Configuration (config.py)
- Discord bot token
- Target channel ID for game screenshots
- Update interval (how often to post new screenshots)
- Emulator speed multiplier
- Emoji to button mappings
- Admin role requirements
- Default ROM file path

## Core Components

### 1. Main Bot (bot.py)
**Purpose**: Discord bot client, event handling, command management

**Key Functions**:
- `on_ready()`: Initialize bot, load emulator, start game loop
- `on_reaction_add(reaction, user)`: Handle emoji reactions and map to game inputs
- `on_reaction_remove(reaction, user)`: Handle reaction removals if needed
- `start_game(ctx, rom_name)`: Admin command to start a game
- `stop_game(ctx)`: Admin command to stop the current game
- `set_speed(ctx, speed)`: Admin command to change emulator speed
- `list_games(ctx)`: List available ROM files
- `game_loop()`: Async loop that runs emulator, captures screenshots, posts to Discord

**Game Loop Flow**:
1. Run emulator for N ticks (based on speed setting)
2. Capture screenshot from PyBoy
3. Delete previous message (if exists)
4. Post new screenshot to Discord channel
5. Add all control emoji reactions to the new message
6. Wait for UPDATE_INTERVAL seconds
7. Repeat

### 2. Emulator Wrapper (emulator.py)
**Purpose**: Manage PyBoy emulator instance

**Class: GameBoyEmulator**
```python
class GameBoyEmulator:
    def __init__(self, rom_path: str, speed: int = 1):
        # Initialize PyBoy with ROM
        
    def tick(self, count: int = 1):
        # Advance emulator by count frames
        
    def press_button(self, button: str):
        # Press a button (up, down, left, right, a, b, start, select)
        
    def release_button(self, button: str):
        # Release a button
        
    def get_screenshot(self) -> Image:
        # Capture current screen as PIL Image
        
    def save_state(self, path: str):
        # Save emulator state
        
    def load_state(self, path: str):
        # Load emulator state
        
    def close(self):
        # Clean up emulator
```

**Features**:
- Initialize PyBoy with ROM file
- Tick emulator forward
- Handle button press/release
- Capture screen buffer as PIL Image
- Save/load states for persistence
- Proper cleanup on shutdown

### 3. Controller (controller.py)
**Purpose**: Map emoji reactions to Game Boy inputs

**Key Data Structures**:
```python
EMOJI_TO_BUTTON = {
    '⬆️': 'up',
    '⬇️': 'down',
    '⬅️': 'left',
    '➡️': 'right',
    '🅰️': 'a',      # or use regional indicator A
    '🅱️': 'b',      # or use regional indicator B
    '▶️': 'start',
    '⏸️': 'select',
}

CONTROL_EMOJIS = list(EMOJI_TO_BUTTON.keys())
```

**Class: InputController**
```python
class InputController:
    def __init__(self, emulator: GameBoyEmulator):
        self.emulator = emulator
        self.input_queue = asyncio.Queue()
        
    async def process_input(self, emoji: str):
        # Map emoji to button and press it
        if emoji in EMOJI_TO_BUTTON:
            button = EMOJI_TO_BUTTON[emoji]
            self.emulator.press_button(button)
            await asyncio.sleep(0.1)  # Hold button briefly
            self.emulator.release_button(button)
            
    async def handle_reaction(self, emoji: str, user: discord.User):
        # Validate input and add to queue
        if user.bot:
            return
        await self.input_queue.put(emoji)
        
    async def process_queue(self):
        # Process inputs from queue
        while True:
            emoji = await self.input_queue.get()
            await self.process_input(emoji)
```

**Features**:
- Map Discord emojis to Game Boy buttons
- Queue system to handle multiple simultaneous inputs
- Input validation
- Configurable button hold duration

### 4. Screenshot Handler (screenshot.py)
**Purpose**: Capture and process game screenshots for Discord

**Key Functions**:
```python
async def capture_screenshot(emulator: GameBoyEmulator) -> io.BytesIO:
    # Get PIL Image from emulator
    image = emulator.get_screenshot()
    
    # Scale up image (Game Boy is 160x144, scale 3x or 4x)
    scaled = image.resize((image.width * 3, image.height * 3), Image.NEAREST)
    
    # Add border/frame if desired
    # Add "watching" user count overlay
    
    # Convert to BytesIO for Discord upload
    buffer = io.BytesIO()
    scaled.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
    
async def add_overlay(image: Image, text: str) -> Image:
    # Add text overlay (e.g., player count, game name)
    pass
```

**Features**:
- Capture screen from PyBoy
- Scale up for better visibility (Game Boy screen is small)
- Use nearest-neighbor scaling to keep pixel-art sharp
- Optional: Add border, game name, viewer count
- Convert to Discord-compatible format

### 5. Utils (utils.py)
**Purpose**: Helper functions

**Functions**:
- `load_rom_list()`: Scan games directory for available ROMs
- `validate_rom(path)`: Check if ROM file is valid
- `is_admin(user, guild)`: Check if user has admin permissions
- `format_game_name(filename)`: Clean up ROM filename for display
- `create_embed(title, description, color)`: Create Discord embeds for messages

## Bot Commands

### Admin Commands (require admin role)
- `/start <game_name>`: Start playing a game
- `/stop`: Stop the current game
- `/speed <1-10>`: Set emulator speed multiplier
- `/reset`: Reset the current game to beginning
- `/savestate <name>`: Save current game state
- `/loadstate <name>`: Load a saved game state

### Public Commands
- `/games`: List available games
- `/help`: Show control instructions
- `/stats`: Show current game stats (uptime, input count, etc.)

## Implementation Details

### Game Loop Architecture
```python
async def game_loop(bot, channel, emulator, controller):
    last_message = None
    
    while bot.is_running:
        try:
            # Tick emulator forward
            for _ in range(bot.config.ticks_per_update):
                emulator.tick()
                
            # Capture screenshot
            screenshot = await capture_screenshot(emulator)
            
            # Delete old message
            if last_message:
                try:
                    await last_message.delete()
                except discord.NotFound:
                    pass
                    
            # Post new screenshot
            file = discord.File(screenshot, filename='game.png')
            last_message = await channel.send(file=file)
            
            # Add reaction controls
            for emoji in CONTROL_EMOJIS:
                await last_message.add_reaction(emoji)
                
            # Wait for next update
            await asyncio.sleep(bot.config.update_interval)
            
        except Exception as e:
            print(f"Error in game loop: {e}")
            await asyncio.sleep(1)
```

### Reaction Handling
```python
@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return
        
    # Check if reaction is on the current game message
    if reaction.message.id != current_game_message_id:
        return
        
    # Process input
    emoji = str(reaction.emoji)
    if emoji in EMOJI_TO_BUTTON:
        await controller.handle_reaction(emoji, user)
        
        # Optional: Remove reaction for cleaner interface
        try:
            await reaction.remove(user)
        except discord.Forbidden:
            pass
```

### Error Handling
- Gracefully handle ROM loading failures
- Recover from Discord API errors (rate limits, permissions)
- Log errors without crashing the bot
- Implement reconnection logic for Discord connection drops
- Handle emulator crashes and restart if needed

## Performance Considerations
1. **Update Interval**: Balance between responsiveness and Discord rate limits (recommend 1-3 seconds)
2. **Image Size**: Scale screenshots appropriately (3x or 4x original size)
3. **Input Queue**: Prevent input spam by using queue with rate limiting
4. **Message Deletion**: Delete old messages to avoid channel clutter
5. **Memory**: Monitor PyBoy memory usage for long-running games

## Security & Best Practices
1. **ROM Files**: Never commit ROM files to git (they're copyrighted)
2. **Bot Token**: Keep token in .env, never commit it
3. **Admin Controls**: Restrict game control commands to admins
4. **Input Validation**: Validate all user inputs and emoji reactions
5. **Rate Limiting**: Implement per-user input rate limits to prevent spam
6. **Error Messages**: Don't expose system paths or sensitive info in error messages

## Deployment Considerations

### For Local Development
- Run on your own machine
- No special requirements beyond Python and dependencies

### For Cloud Deployment (Render/Fly.io)
**Challenges**:
- Bot needs to run 24/7 to stay connected to Discord
- Emulator state needs persistence (save states to volume/database)
- ROM files need to be included in deployment (upload separately)
- Free tiers may have CPU/memory limitations

**Render Setup**:
1. Create a new Web Service (not static site)
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python bot.py`
4. Add environment variables
5. Upload ROM files to persistent disk (if available) or include in repo (private repo only)

**Fly.io Setup**:
1. Create Dockerfile
2. Use fly.toml for configuration
3. Add persistent volume for save states
4. Deploy with `fly deploy`

## Testing Checklist
- [ ] Bot connects to Discord successfully
- [ ] Emulator loads ROM file
- [ ] Screenshots are captured and posted
- [ ] All emoji reactions map to correct buttons
- [ ] Input queue processes commands in order
- [ ] Multiple users can send inputs
- [ ] Admin commands work properly
- [ ] Bot handles disconnections gracefully
- [ ] Save/load states work correctly
- [ ] Game switching works without memory leaks

## Future Enhancements
1. **Voting System**: Require N reactions before input is sent (Twitch Plays style)
2. **Democracy Mode**: Most popular input in time window wins
3. **Anarchy Mode**: All inputs processed immediately
4. **Spectator Count**: Show how many people are watching
5. **Input Cooldown**: Limit inputs per user per time period
6. **Multiple Games**: Support multiple concurrent game sessions in different channels
7. **Leaderboard**: Track who sends most inputs
8. **Stream Integration**: Integrate with Twitch for cross-platform play
9. **Save State Management**: Auto-save at intervals, multiple save slots
10. **Game Library**: Database of games with metadata, screenshots, descriptions

## ROMs and Legal Notice
**IMPORTANT**: This bot requires Game Boy ROM files to function. You must:
- Own the original game cartridge for any ROM you use
- Obtain ROMs through legal means only
- Never distribute ROM files
- Respect intellectual property rights

The bot creator is responsible for ensuring their use complies with copyright law.

## Troubleshooting

### Common Issues
1. **Bot doesn't respond to reactions**: Check if bot has "Read Message History" and "Add Reactions" permissions
2. **Screenshots not posting**: Verify "Attach Files" permission
3. **Emulator crashes**: Ensure ROM file is valid and compatible with PyBoy
4. **High CPU usage**: Reduce emulator speed or increase update interval
5. **Rate limited by Discord**: Increase UPDATE_INTERVAL to avoid hitting limits

## Development Workflow
1. Set up Python virtual environment
2. Install dependencies from requirements.txt
3. Create .env file with bot token and channel ID
4. Add a test ROM to games/ directory
5. Run bot locally: `python bot.py`
6. Test in private Discord server
7. Iterate on features
8. Deploy to cloud when ready

## Success Criteria
- Bot runs stably for 24+ hours without crashes
- Multiple users can control the game simultaneously
- Screenshot updates are smooth and responsive
- Admin commands work reliably
- Game state persists across bot restarts (via save states)
- User experience is fun and engaging

---

**Ready to build!** Use this specification with Claude Code to implement the Discord Game Boy bot. Start with the basic bot structure, then add the emulator wrapper, followed by the game loop and reaction handling.
