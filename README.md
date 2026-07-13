# 👁️ Discord Roblox Sniper Bot

A Discord bot that monitors Roblox users and alerts you when they come online or go offline!

## Features

✨ **Real-time Monitoring** - Checks Roblox user status every 30 seconds  
🟢 **Live Alerts** - Get notified instantly when tracked users come online  
🔴 **Offline Detection** - Know when users go offline  
📋 **Multi-user Tracking** - Track multiple Roblox users simultaneously  
💾 **Persistent Storage** - Tracked users are saved between bot restarts  

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token ([Get here](https://discord.com/developers/applications))
- Roblox usernames to track

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Dejwid303/discord-roblox-sniper.git
cd discord-roblox-sniper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create a `.env` file**
```bash
cp .env.example .env
```

4. **Add your Discord bot token**
Edit `.env` and replace `your_bot_token_here` with your actual bot token:
```
DISCORD_BOT_TOKEN=your_actual_token_here
```

### Getting a Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to the "Bot" tab and click "Add Bot"
4. Under TOKEN, click "Copy" to copy your bot token
5. Paste it in your `.env` file

### Bot Permissions

Make sure your bot has these permissions:
- `Send Messages`
- `Embed Links`
- `Read Messages/View Channels`

## Commands

| Command | Description |
|---------|-------------|
| `!snipe <username>` | Start tracking a Roblox user |
| `!unsnipe <username>` | Stop tracking a user |
| `!sniping` | List all currently tracked users |
| `!status <username>` | Check a user's current online status |
| `!help_sniper` | Show all available commands |

## Usage Examples

```
!snipe BuilderMan           # Start tracking the user "BuilderMan"
!status BuilderMan          # Check if BuilderMan is online right now
!sniping                    # See all tracked users and their status
!unsnipe BuilderMan         # Stop tracking BuilderMan
```

## Running the Bot

```bash
python bot.py
```

You should see output like:
```
✓ Bot logged in as YourBotName#1234
✓ Monitoring 0 Roblox users
```

## How It Works

1. **Track a user** with `!snipe <username>`
2. **Bot verifies** the Roblox username exists
3. **Background task** checks status every 30 seconds
4. **Alerts sent** to the channel where you ran the command when status changes
5. **Data persisted** in `tracked_users.json` (survives bot restarts)

## Data Storage

Tracked users are automatically saved to `tracked_users.json`:
```json
{
  "BuilderMan": 1234567890,
  "PlayerName": 9876543210
}
```

Keys are usernames, values are Discord channel IDs.

## Troubleshooting

### Bot doesn't respond to commands
- Check that the bot is in your Discord server
- Verify the bot has "Send Messages" permission
- Make sure you're using the correct prefix: `!`

### "User not found" error
- Double-check the Roblox username spelling
- Usernames are case-sensitive
- The user may be banned or deleted

### Bot keeps going offline
- Check your internet connection
- Ensure Discord bot token is valid
- Check console for error messages

## Example Alert

When a tracked user comes online:

```
🟢 User Online!
BuilderMan just came online!

Status: Active on Roblox
```

When they go offline:

```
🔴 User Offline
BuilderMan just went offline
```

## License

MIT License - Feel free to use and modify!

## Support

Having issues? Check:
1. Your `.env` file has the correct bot token
2. Bot has proper permissions in the Discord server
3. The Roblox username exists and is spelled correctly
4. Your internet connection is stable

---

**Made with ❤️ for Roblox snipers**
