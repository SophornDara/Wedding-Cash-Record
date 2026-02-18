"""
Wedding Manager Application
Main entry point for the wedding guest management system.
"""

import config
from utils import get_khmer_font
from ui import WeddingApp


def main():
    """Initialize and run the wedding management application."""
    # Detect and set the Khmer font
    detected_font = get_khmer_font()
    config.FONT_NAME = detected_font
    print(f"Using Font: {detected_font}")
    
    # Start the application
    app = WeddingApp()
    app.mainloop()


if __name__ == "__main__":
    main()