"""Application settings and configuration."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_FILE = os.getenv("DB_NAME", "wedding_data.db")

# Application settings
APP_TITLE = os.getenv("APP_TITLE", "Wedding Manager")
FONT_SIZE = int(os.getenv("FONT_SIZE", 12))

# Font name - will be initialized by the main application
FONT_NAME = "Khmer OS Siemreap"  # Default, can be overridden

# --- SYSTEM ENCODING FIX (CRITICAL FOR WINDOWS) ---
# Force Python to treat all output as UTF-8 to prevent "???" in terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
