"""Font detection and configuration utilities."""

import os
from tkinter import font as tkfont


def get_khmer_font():
    """Try to find an available Khmer font on the system.
    
    Returns:
        str: Name of the available Khmer font, or "Arial" as fallback
    """
    try:
        # Priority list of fonts
        khmer_fonts = [
            "Khmer OS Siemreap",
            "Khmer OS Battambang", 
            "Khmer OS Content",
            "DaunPenh",  # Standard Windows font
            "Leelawadee UI",  # Good fallback for Windows
            "Hanuman",
            "Arial"
        ]
        
        import tkinter as tk
        temp_root = tk.Tk()
        temp_root.withdraw()
        available_fonts = tkfont.families(temp_root)
        temp_root.destroy()
        
        # Check environment variable first
        env_font = os.getenv("FONT_NAME", "Khmer OS Siemreap")
        if env_font in available_fonts:
            return env_font
        
        # Check list
        for font_name in khmer_fonts:
            if font_name in available_fonts:
                return font_name
        
        return "Arial"
    except Exception:
        return "Arial"
