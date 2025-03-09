import os
import logging
import servicemanager
import win32serviceutil
import win32service
import win32event
import subprocess
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime
import win32timezone  # Windows-specific timezone handling

# Basic logging setup with explicit time handling
class WindowsLocalFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Get Windows local time directly
        current_time = time.localtime()
        if datefmt:
            return time.strftime(datefmt, current_time)
        return time.strftime('%Y-%m-%d %H:%M:%S', current_time)

# Configure logging
handler = logging.FileHandler('E:/TGOBSYNC/telegram_service.log')
formatter = WindowsLocalFormatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Clear any existing handlers to avoid duplicates
for hdlr in logger.handlers[:]:
    if isinstance(hdlr, logging.StreamHandler):
        logger.removeHandler(hdlr)

class TelegramBotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TelegramDiaryBotService"
    _svc_display_name_ = "Telegram Diary Bot Service"
    _svc_description_ = "Runs a Telegram bot to sync diary messages."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.process = None
        logging.info(f"Service initialized at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    def SvcDoRun(self):
        try:
            logging.info("Service is starting...")
            self.main()
        except Exception as e:
            logging.error(f"Service failed: {str(e)}")
            logging.error(traceback.format_exc())

    def main(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
        python_exe = os.path.join(os.path.dirname(sys.executable), 'python.exe')
        
        logging.info(f"Script path: {script_path}")
        logging.info(f"Python exe: {python_exe}")
        
        while self.running:
            try:
                logging.info(f"Starting bot process with {python_exe}")
                
                # Start the bot as a separate process with output redirection
                self.process = subprocess.Popen(
                    [python_exe, script_path],
                    cwd=os.path.dirname(script_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                logging.info(f"Bot process started with PID: {self.process.pid}")
                
                # Wait for the process to end or service to stop
                while self.running:
                    if self.process.poll() is not None:
                        # Process ended, get output
                        out, err = self.process.communicate()
                        logging.info(f"Bot process output: {out.decode()}")
                        if err:
                            logging.error(f"Bot process error: {err.decode()}")
                        
                        if self.running:
                            logging.info("Bot process ended, waiting before restart...")
                            time.sleep(10)
                            break
                    time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error running bot: {str(e)}")
                logging.error(traceback.format_exc())
                if self.running:
                    time.sleep(10)

    def SvcStop(self):
        logging.info("Service stop requested...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        if self.process:
            self.process.terminate()
        win32event.SetEvent(self.stop_event)
        logging.info("Service stopped")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TelegramBotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(TelegramBotService)
