---
description: Setup daily automated execution on Windows
---

# Windows Task Scheduler Setup for YouTube Agent

This workflow guides you through setting up daily automated execution of the YouTube Agent on Windows.

## Prerequisites

1. Docker Desktop installed and running on Windows
2. Ollama container running: `docker-compose up -d ollama`
3. `.env` file configured with Telegram credentials
4. `storage_state.json` file created (run `python save_state_from_chrome.py` first)

## Setup Steps

### 1. Open Task Scheduler

- Press `Win + R`
- Type `taskschd.msc` and press Enter

### 2. Create Basic Task

- In the right panel, click **"Create Basic Task"**
- **Name**: `YouTube Agent Daily Runner`
- **Description**: `Automated YouTube video selection and Watch Later addition`
- Click **Next**

### 3. Set Trigger

- **Trigger**: Select "Daily"
- Click **Next**
- **Start**: Choose your preferred time (e.g., `07:00 AM`)
- **Recur every**: `1 days`
- Click **Next**

### 4. Set Action

- **Action**: Select "Start a program"
- Click **Next**
- **Program/script**: `docker-compose`
- **Add arguments**: `run --rm orchestrator`
- **Start in**: Full path to your project directory
  - Example: `C:\Users\YourUsername\youtube-agent`
- Click **Next**

### 5. Configure Advanced Settings

After creating the task, right-click it and select **Properties**:

- **General** tab:
  - ✅ Check "Run whether user is logged on or not"
  - ✅ Check "Run with highest privileges" (if Docker requires it)
  - Select "Windows 10" in the "Configure for" dropdown

- **Settings** tab:
  - ✅ Check "Wake the computer to run this task" (optional)
  - **If the task fails, restart every**: `1 hour`
  - **Attempt to restart up to**: `3 times`
  - ✅ Check "Stop the task if it runs longer than": `30 minutes`

### 6. Test Execution

- Right-click the task in Task Scheduler
- Click **"Run"**
- Monitor execution:
  - Check `logs/` directory for output
  - Verify Telegram notification received on iOS
  - Check YouTube Watch Later playlist

## PowerShell Script Alternative

Create `run_daily.ps1` in your project root:

```powershell
# YouTube Agent Daily Runner
# Change to project directory
Set-Location "C:\path\to\youtube-agent"

# Ensure Ollama is running
docker-compose up -d ollama

# Wait for Ollama to be ready
Start-Sleep -Seconds 5

# Run orchestrator
docker-compose run --rm orchestrator

# Log exit code
$exitCode = $LASTEXITCODE
Write-Host "Orchestrator exited with code: $exitCode"

# Exit with same code
exit $exitCode
```

Then schedule this PowerShell script instead:
- **Program/script**: `powershell.exe`
- **Add arguments**: `-ExecutionPolicy Bypass -File "C:\path\to\youtube-agent\run_daily.ps1"`

## Troubleshooting

### Task runs but nothing happens
- Check Event Viewer: `Windows Logs > Application`
- Verify Docker Desktop is set to start on boot
- Check that `docker-compose` is in system PATH

### Notification not received
- Verify `.env` has correct `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Test manually: `docker-compose run --rm orchestrator`
- Check container logs: `docker logs youtube-agent-orchestrator`

### Videos not added to Watch Later
- Verify `DRY_RUN=false` in `.env`
- Check `storage_state.json` is not expired (re-run `save_state_from_chrome.py`)
- Verify mounts in `docker-compose.yml` point to correct files

## Logs

Check logs in the following locations:
- **Orchestrator logs**: `./logs/` directory
- **Docker logs**: `docker logs youtube-agent-orchestrator`
- **Task Scheduler logs**: Task Scheduler > History tab (enable in View menu)
