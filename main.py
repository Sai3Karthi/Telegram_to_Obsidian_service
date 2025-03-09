from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
from datetime import datetime, timedelta
import logging
import calendar
from collections import defaultdict
from typing import Dict, List, Optional
import asyncio
from pathlib import Path
from telegram.error import RetryAfter
import pytz
import sys

# Get local timezone
local_tz = pytz.timezone('Asia/Kolkata')  # For India/IST

class LocalTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.now()
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            s = ct.strftime("%Y-%m-%d %H:%M:%S")
        return s

# Update the logging setup
logger = logging.getLogger()
handler = logging.FileHandler('telegram_bot.log')
formatter = LocalTimeFormatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

TOKEN = '7675657512:AAFFqwYptEB7oTCKPgBisD51svkwJXFQY-Q'
GROUP_ID = '-4757217272'
PC_FOLDER = Path('E:/Vault/SaiLife/MyDiary')
MOBILE_FOLDER = Path('/storage/emulated/0/Obsidian/SaiLife/MyDiary')

class MessageBuffer:
    def __init__(self):
        self.messages: Dict[str, List[dict]] = defaultdict(list)
        self.images: Dict[str, List[dict]] = defaultdict(list)
        self._cache: Dict[str, tuple] = {}
        logging.info("MessageBuffer initialized")

    def add_message(self, chat_id: str, text: str, timestamp: datetime) -> None:
        # Ensure timestamp has timezone info
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=pytz.UTC)
        logging.info(f"Adding message to buffer - Chat ID: {chat_id}, Text: {text}, Time: {timestamp}")
        self.messages[chat_id].append({'text': text, 'timestamp': timestamp})
        self._cache.pop(chat_id, None)

    def add_image(self, chat_id: str, path: str, timestamp: datetime) -> None:
        # Ensure timestamp has timezone info
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=pytz.UTC)
        self.images[chat_id].append({'image_path': path, 'timestamp': timestamp})
        self._cache.pop(chat_id, None)

    def get_content(self, chat_id: str) -> tuple:
        if chat_id not in self._cache:
            self._cache[chat_id] = (self.messages[chat_id], self.images[chat_id])
        logging.info(f"Getting content for {chat_id}. Messages: {len(self.messages[chat_id])}, Images: {len(self.images[chat_id])}")
        return self._cache[chat_id]

    def clear(self, chat_id: str) -> None:
        self.messages[chat_id].clear()
        self.images[chat_id].clear()
        self._cache.pop(chat_id, None)

buffer = MessageBuffer()

def get_adjacent_dates(date: datetime) -> tuple:
    last_day = calendar.monthrange(date.year, date.month)[1]
    prev_date = date - timedelta(days=1) if date.day > 1 else date
    next_date = date + timedelta(days=1) if date.day < last_day else date
    
    # Get 2-digit year
    year_suffix = str(date.year)[-2:]
    prev_year_suffix = str(prev_date.year)[-2:]
    next_year_suffix = str(next_date.year)[-2:]
    
    return (
        f"{prev_date.strftime('%B')}{prev_date.day}'{prev_year_suffix}",
        f"{next_date.strftime('%B')}{next_date.day}'{next_year_suffix}"
    )

def update_md_file(text: List[dict], images: List[dict], folder: Path, message_date: datetime) -> str:
    # Ensure message_date has timezone info
    if message_date.tzinfo is None:
        message_date = message_date.replace(tzinfo=local_tz)
    
    # Use message date instead of current time
    year_suffix = str(message_date.year)[-2:]
    filename = f"{message_date.strftime('%B')}{message_date.day}'{year_suffix}.md"
    filepath = folder / filename
    
    new_content = []
    existing_content = ""
    footer = "\n"
    last_timestamp = None
    
    # Read existing content and find the last timestamp
    if filepath.exists():
        content = filepath.read_text(encoding='utf-8')
        parts = content.split('---')
        existing_content = parts[0].strip()
        footer = f"\n---{parts[1]}" if len(parts) > 1 else "\n"
        
        # Find the last timestamp in existing content
        time_entries = [line for line in existing_content.split('\n') if line.startswith('Neram:')]
        if time_entries:
            try:
                last_time = time_entries[-1].replace('Neram:', '').strip()
                last_timestamp = datetime.strptime(last_time, '%I:%M %p')
                # Set the date and timezone
                last_timestamp = last_timestamp.replace(
                    year=message_date.year, 
                    month=message_date.month, 
                    day=message_date.day
                )
                last_timestamp = local_tz.localize(last_timestamp)
            except ValueError:
                last_timestamp = None
        
        new_content.append(existing_content + "\n\n")
    
    # Process new entries
    for item in sorted(text + images, key=lambda x: x['timestamp']):
        current_timestamp = item['timestamp']
        
        # Convert to local time if timestamp has timezone info
        if current_timestamp.tzinfo is not None:
            current_timestamp = current_timestamp.astimezone()  # Convert to local time
        else:
            # If no timezone info, assume it's local time
            current_timestamp = current_timestamp.replace(tzinfo=message_date.tzinfo)
            
        # Add timestamp if there's more than 15 minutes gap
        if last_timestamp is None or (current_timestamp - last_timestamp).total_seconds() > 900:
            time_str = current_timestamp.strftime('%I:%M %p')
            new_content.append(f"Neram: {time_str}\n")
            last_timestamp = current_timestamp
        
        # Add the content
        if 'image_path' in item:
            new_content.append(f"![[{Path(item['image_path']).name}]]\n\n")
        else:
            new_content.append(f"{item['text']}\n\n")
    
    # Add navigation links if it's a new file
    if not filepath.exists():
        prev_link, next_link = get_adjacent_dates(message_date)
        new_content.append(f"\n---\n[[{prev_link}]] | [[{next_link}]]")
    else:
        new_content.append(footer.rstrip())
    
    try:
        filepath.write_text(''.join(new_content), encoding='utf-8')
        # Set file modification time to local time
        os.utime(filepath, (message_date.timestamp(), message_date.timestamp()))
        return filename
    except Exception as e:
        logging.error(f"Error updating file {filepath}: {str(e)}")
        raise

async def handle_message(update, context) -> None:
    if str(update.message.chat_id) == GROUP_ID:
        text = update.message.text
        timestamp = update.message.date
        
        logging.info(f"Processing message: {text}")
        logging.info(f"Original timestamp: {timestamp}")
        
        logging.info(f"Adding to buffer: {text} at time {timestamp}")
        buffer.add_message(update.message.chat_id, text, timestamp)

async def handle_photo(update, context) -> None:
    if str(update.message.chat_id) != GROUP_ID:
        return
        
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = PC_FOLDER / 'attachments' / filename
    
    await file.download_to_drive(str(filepath))
    buffer.add_image(update.message.chat_id, str(filepath), update.message.date)

async def process_update(update, context, folder: Path) -> None:
    if str(update.message.chat_id) != GROUP_ID:
        return
        
    try:
        logging.info("Starting process_update")
        text_content, image_content = buffer.get_content(update.message.chat_id)
        
        logging.info(f"Processing update with {len(text_content)} text messages and {len(image_content)} images")
        
        if not text_content and not image_content:
            logging.info("No content found in buffer")
            await update.message.reply_text("Edachu entry potutu save panra muttal")
            return
        
        # Log the actual content
        for msg in text_content:
            logging.info(f"Message in buffer: {msg['text']} at {msg['timestamp']}")
        
        # Group messages by date
        date_grouped_content = defaultdict(lambda: {'text': [], 'images': []})
        
        # Group text messages by date
        for msg in text_content:
            # Convert UTC timestamp to local time for grouping
            local_timestamp = msg['timestamp'].astimezone(local_tz)
            date_key = local_timestamp.date()
            logging.info(f"Grouping message for date {date_key}: {msg['text']}")
            date_grouped_content[date_key]['text'].append(msg)
            
        # Group images by date
        for img in image_content:
            local_timestamp = img['timestamp'].astimezone(local_tz)
            date_key = local_timestamp.date()
            date_grouped_content[date_key]['images'].append(img)
            
        # Process each date's content separately
        updated_files = []
        for date_key, content in sorted(date_grouped_content.items()):
            message_date = datetime.combine(date_key, datetime.min.time())
            message_date = local_tz.localize(message_date)  # Add timezone info
            filename = update_md_file(
                content['text'],
                content['images'],
                folder,
                message_date
            )
            updated_files.append(filename)
        
        buffer.clear(update.message.chat_id)
        files_str = ", ".join(updated_files)
        await update.message.reply_text(f"{files_str} la pudhusa potuten sai!")
        
    except Exception as e:
        logging.error(f"Error in process_update: {str(e)}", exc_info=True)
        await update.message.reply_text(f"Error: {str(e)}")

async def update_pc(update, context) -> None:
    logging.info("update_pc command received")
    await process_update(update, context, PC_FOLDER)

async def update_mb(update, context) -> None:
    logging.info("update_mb command received")
    await process_update(update, context, MOBILE_FOLDER)

# Add this new variable
should_stop = False

async def run_bot():
    try:
        logging.info("Starting Telegram bot...")
        
        # Test bot token first
        logging.info("Testing bot token...")
        bot = Bot(TOKEN)
        try:
            me = await bot.get_me()
            logging.info(f"Bot connection successful - @{me.username}")
        except Exception as e:
            logging.error(f"Failed to connect to bot: {e}")
            raise
            
        logging.info("Initializing application...")
        app = Application.builder().token(TOKEN).build()
        
        logging.info("Creating directories...")
        (PC_FOLDER / 'attachments').mkdir(parents=True, exist_ok=True)
        (MOBILE_FOLDER / 'attachments').mkdir(parents=True, exist_ok=True)
        
        logging.info("Adding handlers...")
        # Add handlers with explicit logging
        app.add_handler(CommandHandler("update_pc", update_pc))
        app.add_handler(CommandHandler("update_mb", update_mb))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        logging.info("Initializing application...")
        await app.initialize()
        logging.info("Starting application...")
        await app.start()
        
        logging.info("Bot started, waiting for messages...")
        
        # Use a longer polling timeout and explicit error handling
        offset = None
        while True:
            try:
                logging.info("Waiting for updates...")
                updates = await app.bot.get_updates(
                    offset=offset,
                    timeout=30,  # Reduced timeout for testing
                    allowed_updates=['message']
                )
                
                logging.info(f"Received {len(updates)} updates")
                for update in updates:
                    offset = update.update_id + 1
                    logging.info(f"Processing update ID: {update.update_id}")
                    await app.process_update(update)
                    
            except Exception as e:
                logging.error(f"Error in update loop: {str(e)}", exc_info=True)
                await asyncio.sleep(5)
                
    except Exception as e:
        logging.error(f"Error in run_bot: {str(e)}", exc_info=True)
        raise

def stop_bot():
    global should_stop
    should_stop = True

def start_bot():
    """Entry point for the Windows service"""
    try:
        # Set up logging
        logging.basicConfig(
            filename='E:/TGOBSYNC/bot.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        logging.info("Bot starting...")
        
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the bot
        loop.run_until_complete(run_bot())
        
    except Exception as e:
        logging.error(f"Error in start_bot: {str(e)}")
        logging.error("Exception traceback:", exc_info=True)

if __name__ == '__main__':
    try:
        # Set up logging to both file and console
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('telegram_bot.log', mode='w'),  # 'w' mode to start fresh
                logging.StreamHandler(sys.stdout)  # Print to console too
            ]
        )
        
        logging.info("=== Starting bot in direct mode ===")
        logging.info(f"Current directory: {os.getcwd()}")
        logging.info(f"Python version: {sys.version}")
        logging.info(f"Bot token: {TOKEN}")
        logging.info(f"Group ID: {GROUP_ID}")
        
        try:
            asyncio.run(run_bot())
        except KeyboardInterrupt:
            logging.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logging.error(f"Error in main: {str(e)}", exc_info=True)
    finally:
        logging.info("Bot shutdown complete")
        input("Press Enter to exit...")  # Keep window open to see error