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

# --- SYSTEM ENCODING FIX (CRITICAL FOR WINDOWS) ---
# Force Python to treat all output as UTF-8 to prevent "???" in terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Font name - detect available Khmer font
# Import here to avoid circular dependencies
from utils.font_utils import get_khmer_font
FONT_NAME = get_khmer_font()
print(f"[Config] Detected Font: {FONT_NAME}")
