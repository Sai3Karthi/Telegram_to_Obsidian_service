# Telegram to Obsidian Service

A cross-platform service that syncs Telegram group messages to Obsidian markdown files. The bot automatically creates daily notes and handles both text messages and images.

## Features

- **Cross-platform**: Works on Windows, Linux, and macOS
- **Secure configuration**: Uses environment variables and config files instead of hardcoded tokens
- **Runs as a service**: Windows service support with Linux daemon functionality
- **Auto-sync**: Syncs messages from a Telegram group to Obsidian vault
- **Daily notes**: Creates daily notes with timestamps and navigation links
- **Media support**: Handles images and attachments
- **Auto-restart**: Restarts automatically on crashes
- **Configurable paths**: Supports both absolute and relative paths for vault locations

## Prerequisites

- Python 3.7 or higher
- Obsidian installed (optional, but recommended for viewing notes)
- A Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Admin access to the target Telegram group

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Sai3Karthi/Telegram_to_Obsidian_service.git
   cd Telegram_to_Obsidian_service
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   - Copy the example configuration:
     ```bash
     cp config.example.py config.py
     ```
   - Edit `config.py` and replace the placeholder values:
     ```python
     BOT_TOKEN = "your-telegram-bot-token"  # Get this from @BotFather
     GROUP_CHAT_ID = "-1234567890"  # Your Telegram group chat ID
     PC_FOLDER = "./vault/MyDiary"  # Your PC Obsidian path
     MOBILE_FOLDER = "./vault_mobile/MyDiary"  # Your mobile sync path (optional)
     ```

4. **Test the installation:**
   ```bash
   python test_fixes.py
   ```

5. **Run the service:**
   
   **Direct mode (for testing):**
   ```bash
   python main.py
   ```
   
   **Service mode:**
   - **Windows:**
     ```bash
     python telegram_service.py install
     python telegram_service.py start
     ```
   - **Linux/macOS:**
     ```bash
     python telegram_service.py start
     ```

## Configuration Details

### Getting Your Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow instructions to create bot
4. Copy the provided token

### Finding Your Group Chat ID
1. Add your bot to the target group
2. Make it an admin
3. Send a message in the group
4. Visit: `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
5. Look for `"chat":{"id": -xxxx}` in the response

### Environment Variables (Alternative to config.py)
You can also use environment variables instead of editing config.py:
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_GROUP_ID="-your-group-id"
export LOCAL_TIMEZONE="Asia/Kolkata"
export PC_FOLDER="./vault/MyDiary"
export MOBILE_FOLDER="./vault_mobile/MyDiary"
```

### Setting Up Paths
1. **PC_FOLDER**: Your main Obsidian vault path
   ```python
   PC_FOLDER = "./vault/MyDiary"  # Relative path (recommended)
   # or
   PC_FOLDER = "/home/user/Obsidian/MyDiary"  # Absolute path
   ```

2. **MOBILE_FOLDER**: (Optional) Path for mobile sync
   ```python
   MOBILE_FOLDER = "./vault_mobile/MyDiary"
   ```

## Service Management

### Windows
Start the service:
```bash
python telegram_service.py start
```

Stop the service:
```bash
python telegram_service.py stop
```

Restart the service:
```bash
python telegram_service.py restart
```

Remove the service:
```bash
python telegram_service.py remove
```

### Linux/macOS
Start the service:
```bash
python telegram_service.py start
```

Stop the service:
```bash
# Use Ctrl+C to stop the service
```

## Bot Commands

The bot responds to these commands in your Telegram group:

- `/update_pc` - Save buffered messages to PC vault
- `/update_mb` - Save buffered messages to mobile vault

## Logging

Logs are stored in the `logs/` directory:
- **Bot logs**: `logs/telegram_bot.log`
- **Service logs**: `logs/telegram_service.log`

You can customize log paths in `config.py`.

## File Structure

```
telegram-to-obsidian-service/
├── main.py                 # Main bot logic
├── telegram_service.py     # Service wrapper (Windows/Linux)
├── config.py              # Configuration file (create from config.example.py)
├── config.example.py      # Configuration template
├── requirements.txt       # Python dependencies
├── test_fixes.py          # Test script
├── README.md             # This file
├── .gitignore            # Git ignore rules
└── logs/                 # Log files directory
    ├── telegram_bot.log
    └── telegram_service.log
```

## Troubleshooting

1. **Service won't start:**
   - Check logs in `logs/telegram_service.log`
   - Verify Python path in service configuration
   - Run `python test_fixes.py` to check configuration
   - On Windows, run as administrator

2. **Messages not syncing:**
   - Verify bot token in configuration
   - Check group chat ID is correct
   - Ensure bot has admin rights in group
   - Verify Obsidian vault paths exist
   - Check `logs/telegram_bot.log` for errors

3. **Network connection errors:**
   - Check internet connectivity
   - Verify firewall isn't blocking the application
   - Check if proxy settings are needed

4. **Wrong timestamps:**
   - Verify system timezone is set correctly
   - Check `LOCAL_TIMEZONE` setting in config.py

5. **Permission errors:**
   - Ensure the application has write permissions to vault directories
   - Check log directory permissions

## Security Notes

- **Never commit your `config.py` file** to version control (it's in .gitignore)
- Use environment variables for production deployments
- Keep your bot token secure and never share it publicly
- Regularly rotate your bot token if needed

## Contributing

Feel free to submit issues and pull requests.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [pywin32](https://github.com/mhammond/pywin32) (Windows only)
- [Obsidian](https://obsidian.md/)
