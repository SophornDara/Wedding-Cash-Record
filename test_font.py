"""Quick test to verify Khmer font loading."""

import sys
print(f"Python encoding: {sys.stdout.encoding}")

from utils.font_utils import get_khmer_font

font_name = get_khmer_font()
print(f"\n✓ Detected Font: {font_name}")

# Test Khmer text
test_text = "ឈ្មោះភ្ញៀវ - Guest Name"
print(f"✓ Test Khmer text: {test_text}")

# Create a simple Tkinter window to test
import tkinter as tk
from tkinter import font as tkfont

root = tk.Tk()
root.withdraw()

# Check if our font is available
available_fonts = tkfont.families(root)
if font_name in available_fonts:
    print(f"✓ Font '{font_name}' is available in Tkinter!")
else:
    print(f"✗ Font '{font_name}' NOT found in Tkinter")
    print(f"Available fonts containing 'Siem' or 'Khmer': {[f for f in available_fonts if 'siem' in f.lower() or 'khmer' in f.lower()]}")

# Test creating a Text widget with the font
try:
    text_widget = tk.Text(root, font=(font_name, 14))
    text_widget.insert("1.0", test_text)
    retrieved = text_widget.get("1.0", "end-1c")
    if retrieved == test_text:
        print(f"✓ Text widget successfully stores Khmer text!")
    else:
        print(f"✗ Text widget corrupted text: {retrieved}")
except Exception as e:
    print(f"✗ Error creating text widget: {e}")

root.destroy()
print("\n✓ Font test completed!")
