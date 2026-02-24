"""Custom message dialog box with Khmer language support."""

import customtkinter as ctk
from tkinter import Toplevel
import config


class KhmerMessageBox:
    """Custom message dialog box with Khmer font support."""
    
    @staticmethod
    def show_message(parent, title, message, msg_type="info"):
        """Display a custom message dialog.
        
        Args:
            parent: Parent window
            title (str): Dialog title
            message (str): Message to display
            msg_type (str): Message type - "info", "error", or "warning"
        """
        dialog = Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        label = ctk.CTkLabel(
            dialog, 
            text=message,
            font=(config.FONT_NAME, 14),
            wraplength=350
        )
        label.pack(pady=30, padx=20)
        
        # Set button color based on message type
        btn_color = "#3498db" if msg_type == "info" else (
            "#e74c3c" if msg_type == "error" else "#f39c12"
        )
        
        ok_btn = ctk.CTkButton(
            dialog,
            text="យល់ព្រម (OK)",
            font=(config.FONT_NAME, 12),
            fg_color=btn_color,
            width=120,
            height=35,
            command=dialog.destroy
        )
        ok_btn.pack(pady=10)
        
        dialog.bind('<Return>', lambda e: dialog.destroy())
        ok_btn.focus()
        parent.wait_window(dialog)

    @staticmethod
    def show_confirm(parent, title, message):
        """Display a confirmation dialog.
        
        Args:
            parent: Parent window
            title (str): Dialog title
            message (str): Message to display
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        result = [False]  # Use list to store result from nested function
        
        dialog = Toplevel(parent)
        dialog.title(title)
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (420 // 2)
        y = (dialog.winfo_screenheight() // 2) - (220 // 2)
        dialog.geometry(f"420x220+{x}+{y}")
        
        label = ctk.CTkLabel(
            dialog, 
            text=message,
            font=(config.FONT_NAME, 14),
            wraplength=370
        )
        label.pack(pady=30, padx=20)
        
        def on_yes():
            result[0] = True
            dialog.destroy()
        
        def on_no():
            result[0] = False
            dialog.destroy()
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        yes_btn = ctk.CTkButton(
            btn_frame,
            text="✓ យល់ព្រម (Yes)",
            font=(config.FONT_NAME, 12),
            fg_color="#10b981",
            hover_color="#059669",
            width=140,
            height=40,
            command=on_yes
        )
        yes_btn.pack(side="left", padx=10)
        
        no_btn = ctk.CTkButton(
            btn_frame,
            text="✕ បោះបង់ (No)",
            font=(config.FONT_NAME, 12),
            fg_color="#6b7280",
            hover_color="#4b5563",
            width=140,
            height=40,
            command=on_no
        )
        no_btn.pack(side="left", padx=10)
        
        dialog.bind('<Return>', lambda e: on_yes())
        dialog.bind('<Escape>', lambda e: on_no())
        yes_btn.focus()
        parent.wait_window(dialog)
        
        return result[0]
