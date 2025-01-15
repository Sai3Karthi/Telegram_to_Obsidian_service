# Telegram_to_Obsidian_service
This is a windows service that lets you use a telegram group as a personal diary that logs the messages to obsidian with custom links and dates.
# Telegram Diary Bot

A Windows service that syncs Telegram group messages to Obsidian markdown files. The bot automatically creates daily notes and handles both text messages and images.

## Features
- Runs as a Windows service
- Syncs messages from a Telegram group to Obsidian vault
- Creates daily notes with timestamps
- Handles images and attachments
- Maintains navigation links between daily notes
- Auto-restarts on crashes

## Prerequisites
- Windows OS
- Python 3.x
- Obsidian installed
- A Telegram Bot Token
- Admin access to the target Telegram group

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/telegram-diary-bot
   cd telegram-diary-bot
2. Install required packages:
   ```bash
   pip install python-telegram-bot pywin32

3. Configure the bot:
   - Open `main.py` and replace these values:
   ```python
   TOKEN = "your-telegram-bot-token"  # Get this from @BotFather
   CHAT_ID = -1234567890  # Your Telegram group chat ID
   PC_FOLDER = Path("C:/Users/YourUsername/Documents/ObsidianVault/DiaryFolder")  # Your PC Obsidian path
   MOBILE_FOLDER = Path("D:/Mobile/ObsidianVault/DiaryFolder")  # Your mobile sync path (if needed)
   ```

4. Install and start the service:
   ```bash
   python telegram_service.py install
   python telegram_service.py start

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

### Setting Up Paths
1. PC_FOLDER: Your Obsidian vault path on the main computer
   ```python
   PC_FOLDER = Path("C:/Users/YourUsername/Documents/ObsidianVault/DiaryFolder")
   ```

2. MOBILE_FOLDER: (Optional) Path for mobile sync
   ```python
   MOBILE_FOLDER = Path("D:/Mobile/ObsidianVault/DiaryFolder")
   ```

## Service Management

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

## Logging

Logs are stored in:
- Service logs: `E:/cursor/telegram_service.log`
- Bot logs: `E:/cursor/bot.log`

You can modify log paths in both `main.py` and `telegram_service.py`.

## File Structure
telegram-diary-bot/
├── main.py # Main bot logic
├── telegram_service.py # Windows service wrapper
├── README.md # This file
└── requirements.txt # Python dependencies

## Troubleshooting

1. Service won't start:
   - Check logs in `telegram_service.log`
   - Verify Python path
   - Run as administrator

2. Messages not syncing:
   - Verify bot token
   - Check group chat ID
   - Ensure bot has admin rights in group
   - Verify Obsidian paths exist

3. Wrong timestamps:
   - Verify system timezone is set correctly
   - Check Windows time settings

## Contributing

Feel free to submit issues and pull requests.

## License

[MIT License](LICENSE)

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [pywin32](https://github.com/mhammond/pywin32)
- [Obsidian](https://obsidian.md/)
   


