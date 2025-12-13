# YouTube Agent - Automated Daily Video Curation

Custom agent that automatically selects and adds YouTube videos to your Watch Later playlist based on AI criteria, running daily in headless mode with iOS notifications.

## Features

- 🤖 **AI-Powered Selection**: Uses local Ollama (Llama 3.2) to intelligently select 1-3 videos from your YouTube homepage
- 📱 **iOS Notifications**: Telegram Bot integration sends instant push notifications with selected videos
- ⏰ **Automated Daily Execution**: Runs automatically on Windows via Task Scheduler
- 🔒 **Privacy-First**: Local LLM model, no API costs, your data stays on your machine
- 🎯 **Headless Operation**: Runs in background with Playwright browser automation
- 🐳 **Containerized**: Docker-based deployment for consistency

## Prerequisites

- **Windows** desktop (always connected to power and internet)
- **Docker Desktop** for Windows
- **Python 3.8+** (for initial setup scripts)
- **Chrome browser** (for YouTube authentication)
- **iOS device** with Telegram app (for notifications)

## Setup Instructions

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env and fill in:
# - PROFILE: Path to your Chrome profile (see below)
# - STATE_FILE: storage_state.json (default)
# - TELEGRAM_BOT_TOKEN: Get from @BotFather (see step 3)
# - TELEGRAM_CHAT_ID: Get from bot after messaging (see step 3)
# - DRY_RUN: false (to enable YouTube actions)
```

**Finding your Chrome Profile path (Windows)**:
```
C:\Users\[YourUsername]\AppData\Local\Google\Chrome\User Data\Default
```

### 3. Setup Telegram Bot (for iOS Notifications)

1. **Create Bot**:
   - Open Telegram on iOS and search for `@BotFather`
   - Send `/newbot` command
   - Follow prompts to name your bot
   - Copy the **bot token** → add to `.env` as `TELEGRAM_BOT_TOKEN`

2. **Get Chat ID**:
   - Start a conversation with your new bot (send any message)
   - Open in browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":123456789}` in the JSON response
   - Copy the **chat ID** → add to `.env` as `TELEGRAM_CHAT_ID`

### 4. Save YouTube Session

```bash
# This will open Chrome with your profile
python save_state_from_chrome.py

# Make sure you're logged into YouTube
# Press Enter when done → saves to storage_state.json
```

### 5. Build and Start Services

```bash
# Start Ollama container (keeps running 24/7)
docker-compose up -d ollama

# Wait for Ollama to download the model (first time only)
# This may take a few minutes

# Test the orchestrator manually
docker-compose run --rm orchestrator
```

### 6. Test Notification

```bash
# Test Telegram notification
python notifier.py

# Check your iOS device for test notification
```

### 7. Schedule Daily Execution

See the detailed workflow: [.agent/workflows/schedule.md](.agent/workflows/schedule.md)

**Quick summary**:
1. Open Task Scheduler (`Win + R`, type `taskschd.msc`)
2. Create Basic Task → Name: "YouTube Agent Daily Runner"
3. Trigger: Daily at your preferred time (e.g., 7:00 AM)
4. Action: Start a program
   - Program: `docker-compose`
   - Arguments: `run --rm orchestrator`
   - Start in: `C:\path\to\youtube-agent`
5. Configure advanced settings (run whether logged in or not)

## Usage

### Manual Execution

```bash
# Scrape YouTube homepage
python youtube_actions.py

# Run full workflow (scrape + select + add to Watch Later + notify)
docker-compose run --rm orchestrator
```

### Testing Modes

```bash
# Dry run (no YouTube actions, just shows what would be added)
# Set DRY_RUN=true in .env
docker-compose run --rm orchestrator

# Production (actually adds videos to Watch Later)
# Set DRY_RUN=false in .env
docker-compose run --rm orchestrator
```

### View Logs

```bash
# Docker logs
docker logs youtube-agent-orchestrator

# Local logs directory
# Check ./logs/ folder for execution history
```

## Architecture

```
┌─────────────────────┐
│ Windows Desktop     │
│ (Always On)         │
└──────────┬──────────┘
           │
    Task Scheduler
           │
           ▼
┌─────────────────────────────┐
│ Docker Compose              │
│                             │
│  ┌──────────────┐          │
│  │ Ollama       │          │
│  │ (Llama 3.2)  │◄─────┐   │
│  └──────────────┘      │   │
│                        │   │
│  ┌──────────────────┐  │   │
│  │ Orchestrator     │──┘   │
│  │ - Scraper        │      │
│  │ - AI Selection   │      │
│  │ - Watch Later    │      │
│  │ - Notifier       │      │
│  └──────────────────┘      │
└─────────────────────────────┘
           │
           ├──► YouTube (Watch Later)
           │
           └──► Telegram Bot API
                      │
                      ▼
              ┌──────────────┐
              │ iOS Device   │
              │ Notification │
              └──────────────┘
```

## Configuration

### System Instructions

Edit `system_instructions.md` to customize the AI's video selection criteria. This file is gitignored by default so you can personalize it.

Example criteria:
- Technical/educational content
- Specific channels you follow
- Video length preferences
- Topics of interest

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434` |
| `OLLAMA_MODEL` | LLM model to use | `llama3.2:3b` |
| `DRY_RUN` | Test mode (no YouTube actions) | `false` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | (required) |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | (required) |
| `STATE_FILE` | Playwright session file | `storage_state.json` |

## Troubleshooting

### "Could not find Save button"
- YouTube UI may have changed → check `youtube_actions.py` selectors
- Session may be expired → re-run `save_state_from_chrome.py`

### Telegram notification not received
- Verify bot token and chat ID in `.env`
- Test manually: `docker-compose run --rm orchestrator`
- Check bot conversation in Telegram app

### Task Scheduler doesn't run
- Ensure Docker Desktop starts on boot
- Check Task Scheduler event logs
- Verify `docker-compose` is in system PATH

### Videos already in Watch Later
- This is normal if you've watched the YouTube homepage before
- The agent can only select from what's currently on your homepage

### Session expires frequently
- Re-run `save_state_from_chrome.py` periodically
- Future enhancement: automatic session refresh

## Development

### Project Structure

```
youtube-agent/
├── youtube_actions.py       # Playwright scraper + Watch Later action
├── notifier.py              # Telegram notification sender
├── save_state_from_chrome.py # Initial authentication setup
├── system_instructions.md   # AI selection criteria (gitignored)
├── docker-compose.yml       # Container orchestration
├── orchestrator/
│   ├── agent_runner.py      # Main workflow coordinator
│   ├── mcp_server.py        # MCP tool wrapper (future use)
│   ├── Dockerfile           # Orchestrator container
│   └── requirements.txt     # Python dependencies
├── data/
│   ├── scraped.json         # Raw YouTube homepage data
│   └── selected.json        # AI-selected videos
├── logs/                    # Execution logs
└── .agent/
    └── workflows/
        └── schedule.md      # Windows Task Scheduler setup

```

### Adding new features

1. **Custom AI Models**: Change `OLLAMA_MODEL` in docker-compose.yml
2. **More Videos**: Edit schema in `agent_runner.py` to select more than 3
3. **Different Actions**: Modify `youtube_actions.py` to like/comment/subscribe
4. **Additional Notifications**: Add email/Slack in `notifier.py`

## Contributing

This is a personal automation project. Feel free to fork and customize for your own use case.

## License

MIT License - Use freely, no warranty provided.