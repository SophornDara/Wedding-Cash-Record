"""Custom message dialog box with Khmer language support."""

import customtkinter as ctk
from tkinter import Toplevel
from config import FONT_NAME


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
            font=(FONT_NAME, 14),
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
            font=(FONT_NAME, 12),
            fg_color=btn_color,
            width=120,
            height=35,
            command=dialog.destroy
        )
        ok_btn.pack(pady=10)
        
        dialog.bind('<Return>', lambda e: dialog.destroy())
        ok_btn.focus()
        parent.wait_window(dialog)
