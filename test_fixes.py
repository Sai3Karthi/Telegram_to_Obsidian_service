#!/usr/bin/env python3
"""
Test script to validate the Telegram to Obsidian service fixes
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import telegram
        print("✓ telegram module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import telegram: {e}")
        return False
    
    try:
        import pytz
        print("✓ pytz module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pytz: {e}")
        return False
    
    try:
        from pathlib import Path
        print("✓ pathlib module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pathlib: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from config import BOT_TOKEN, GROUP_CHAT_ID, LOCAL_TIMEZONE, PC_FOLDER, MOBILE_FOLDER
        print("✓ Configuration loaded successfully")
        print(f"  - Bot token: {BOT_TOKEN[:10]}...")
        print(f"  - Group ID: {GROUP_CHAT_ID}")
        print(f"  - Timezone: {LOCAL_TIMEZONE}")
        print(f"  - PC Folder: {PC_FOLDER}")
        print(f"  - Mobile Folder: {MOBILE_FOLDER}")
        return True
    except ImportError as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def test_directory_creation():
    """Test that directories can be created"""
    print("\nTesting directory creation...")
    try:
        from config import PC_FOLDER, MOBILE_FOLDER
        
        pc_path = Path(PC_FOLDER)
        mobile_path = Path(MOBILE_FOLDER)
        
        # Create test directories
        (pc_path / 'attachments').mkdir(parents=True, exist_ok=True)
        (mobile_path / 'attachments').mkdir(parents=True, exist_ok=True)
        
        if (pc_path / 'attachments').exists():
            print("✓ PC attachments directory created successfully")
        else:
            print("✗ Failed to create PC attachments directory")
            return False
            
        if (mobile_path / 'attachments').exists():
            print("✓ Mobile attachments directory created successfully")
        else:
            print("✗ Failed to create mobile attachments directory")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Directory creation failed: {e}")
        return False

def test_logging():
    """Test logging configuration"""
    print("\nTesting logging...")
    try:
        import logging
        from config import BOT_LOG_FILE, SERVICE_LOG_FILE
        
        # Create log directories
        Path(BOT_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(SERVICE_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        # Test logging to file
        logger = logging.getLogger('test')
        handler = logging.FileHandler(BOT_LOG_FILE)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        logger.info("Test log message")
        
        if Path(BOT_LOG_FILE).exists():
            print("✓ Logging configuration works")
            print(f"  - Bot log file: {BOT_LOG_FILE}")
            print(f"  - Service log file: {SERVICE_LOG_FILE}")
            return True
        else:
            print("✗ Log file was not created")
            return False
            
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False

def test_cross_platform():
    """Test cross-platform compatibility"""
    print("\nTesting cross-platform compatibility...")
    try:
        # Test path handling
        from pathlib import Path
        test_path = Path("./test/path")
        print(f"✓ Path handling works: {test_path}")
        
        # Test OS detection
        import os
        if os.name == 'nt':
            print("✓ Running on Windows")
        else:
            print("✓ Running on Unix-like system")
        
        return True
    except Exception as e:
        print(f"✗ Cross-platform test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Telegram to Obsidian Service Tests ===\n")
    
    tests = [
        test_imports,
        test_config,
        test_directory_creation,
        test_logging,
        test_cross_platform
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application is ready to use.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())