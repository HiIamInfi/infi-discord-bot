# Infi Discord Bot

A modular Discord bot built with discord.py featuring AI chat, collaborative video watching, and moderation tools.

## Features

### AI Chat (`/ask`)
Ask questions to Google Gemini AI directly in Discord. Supports long responses (auto-split) and contextual replies when you reply to a message and mention the bot.

### Watch Together (`/watch`)
Create Watch2Gether rooms for synchronized group video watching. Optionally preload a YouTube or other video URL.

### Moderation (`/purge`)
Bulk delete messages in a channel with a confirmation prompt. Requires `manage_messages` permission.

### Utilities
- `/ping` - Check bot latency
- `/info` - Bot status, uptime, and connected servers
- `/sync` - Sync slash commands (owner only)

### Admin Commands (Owner Only)
Text commands for bot management:
- `!load/unload/reload <cog>` - Manage cogs at runtime
- `!cogs` - List loaded cogs
- `!shutdown` - Gracefully stop the bot

## Deployment

### Quick Start with Docker

1. Copy the example compose file:
   ```bash
   curl -O https://raw.githubusercontent.com/hiiaminfi/infi-discord-bot/main/docker-compose.example.yml
   mv docker-compose.example.yml docker-compose.yml
   ```

2. Edit `docker-compose.yml` and add your tokens:
   ```yaml
   environment:
     - DISCORD_TOKEN=your_actual_token
     - GEMINI_API_KEY=your_gemini_key  # optional
   ```

3. Start the bot:
   ```bash
   docker compose up -d
   ```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | Yes | Your Discord bot token |
| `DISCORD_OWNER_IDS` | No | Comma-separated user IDs for bot owners |
| `DISCORD_PREFIX` | No | Text command prefix (default: `!`) |
| `GEMINI_API_KEY` | No | Google AI Studio API key for `/ask` |
| `W2G_API_KEY` | No | Watch2Gether API key (higher rate limits) |
| `ENVIRONMENT` | No | `development` or `production` |
| `DEBUG` | No | Enable debug logging |

### Data Persistence

The bot stores data in `/app/data/` inside the container:
- `bot.db` - SQLite database (command logs, future features)
- `system_prompt.txt` - Custom Gemini system prompt (optional)

Mount a volume to persist data:
```yaml
volumes:
  - ./data:/app/data
```

### Building from Source

```bash
git clone https://github.com/hiiaminfi/infi-discord-bot.git
cd infi-discord-bot
docker build -t infi-discord-bot .
```

Or run locally:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit with your tokens
python -m bot.main
```

## Getting API Keys

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application → Bot → Reset Token
3. Enable "Message Content Intent" under Privileged Gateway Intents

### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key

### Watch2Gether API Key (Optional)
1. Visit [Watch2Gether](https://w2g.tv)
2. Contact them for API access

## License

MIT
