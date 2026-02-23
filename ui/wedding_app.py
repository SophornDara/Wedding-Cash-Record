"""Main application window for Wedding Manager."""

import sqlite3
import tkinter as tk
import customtkinter as ctk
import pandas as pd
import config
from database import WeddingDB
from utils import khmer_to_arabic
from .message_box import KhmerMessageBox


class WeddingApp(ctk.CTk):
    """Main application window for wedding guest management."""
    
    def __init__(self):
        """Initialize the application window."""
        super().__init__()
        self.db = WeddingDB()

        self.title(config.APP_TITLE)
        self.geometry("1200x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Fonts - use config module for dynamic font detection
        self.khmer_font = (config.FONT_NAME, config.FONT_SIZE)
        self.header_font = (config.FONT_NAME, 24, "bold")
        
        print(f"[WeddingApp] Using Font: {config.FONT_NAME}, Size: {config.FONT_SIZE}")
        
        # Global Font Setting for CTk
        try:
            ctk.FontManager.load_font(config.FONT_NAME)
        except Exception:
            pass 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.refresh_data()

    def setup_sidebar(self):
        """Setup the sidebar with input fields and buttons."""
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="បញ្ចូលព័ត៌មាន", font=self.header_font).pack(pady=(30, 20))

        self.name_entry = self.create_input("ឈ្មោះភ្ញៀវ (Name)")
        self.khr_entry = self.create_input("ប្រាក់រៀល (KHR៛)")
        self.usd_entry = self.create_input("ប្រាក់ដុល្លារ (USD $)")
        self.addr_entry = self.create_input("អាសយដ្ឋាន (Address)")

        save_btn = ctk.CTkButton(
            self.sidebar, 
            text="រក្សាទុក (Save)", 
            font=self.khmer_font, 
            height=45, 
            fg_color="#2ecc71", 
            hover_color="#27ae60", 
            command=self.save_guest
        )
        save_btn.pack(padx=20, pady=(20, 10), fill="x")

        export_btn = ctk.CTkButton(
            self.sidebar, 
            text="ទាញយក Excel", 
            font=self.khmer_font, 
            height=40, 
            fg_color="#F54927", 
            hover_color="#F54927", 
            command=self.export_excel
        )
        export_btn.pack(padx=20, pady=5, fill="x")

    def create_input(self, placeholder):
        """Create an input field with label using native tkinter Text widget.
        
        Args:
            placeholder (str): Label text for the input field
            
        Returns:
            tk.Text: The created text input widget
        """
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(padx=20, pady=5, fill="x")
        
        label = ctk.CTkLabel(
            frame, 
            text=placeholder, 
            font=(config.FONT_NAME, 11), 
            text_color="gray60", 
            anchor="w"
        )
        label.pack(fill="x")
        
        # Use native tkinter Text widget for proper Khmer support
        textbox = tk.Text(
            frame,
            font=(config.FONT_NAME, config.FONT_SIZE),
            height=2,
            width=30,
            wrap="none",
            bg="#343638",  # Dark background to match CTk theme
            fg="white",    # White text
            insertbackground="white",  # White cursor
            relief="flat",
            padx=10,
            pady=8
        )
        textbox.pack(fill="x", pady=(2, 5))
        
        # Disable return key creating new lines
        textbox.bind("<Return>", lambda e: "break")
        
        return textbox
    
    def get_input_text(self, textbox):
        """Get text from a tkinter Text widget.
        
        Args:
            textbox (tk.Text): The textbox to read from
            
        Returns:
            str: The trimmed text content
        """
        return textbox.get("1.0", "end-1c").strip()
    
    def clear_textbox(self, textbox):
        """Clear content from a tkinter Text widget.
        
        Args:
            textbox (tk.Text): The textbox to clear
        """
        textbox.delete("1.0", "end")

    def setup_main_area(self):
        """Setup the main display area with table and statistics."""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.stats_label = ctk.CTkLabel(
            self.main_frame, 
            text="", 
            font=(config.FONT_NAME, 18, "bold")
        )
        self.stats_label.pack(pady=10)

        # Header Frame
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="#e0e0e0", height=45)
        header_frame.pack(fill="x", pady=(10, 0))
        header_frame.pack_propagate(False)
        
        headers = ["ល.រ", "ឈ្មោះ", "ប្រាក់រៀល", "ប្រាក់ដុល្លារ$", "អាសយដ្ឋាន address"]
        widths = [60, 200, 150, 150, 200]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                header_frame, 
                text=header, 
                font=(config.FONT_NAME, 13, "bold"),
                text_color="black",
                width=width
            )
            label.pack(side="left", padx=5, pady=8)
        
        self.table_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color="white",
            scrollbar_button_color="#3498db"
        )
        self.table_frame.pack(fill="both", expand=True)
        
        self.column_widths = widths

    def create_table_row(self, row_data, row_index):
        """Create a row in the data table.
        
        Args:
            row_data (tuple): Data for the row
            row_index (int): Index of the row for alternating colors
        """
        bg_color = "#f8f9fa" if row_index % 2 == 0 else "white"
        
        row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color, height=45)
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)
        
        for i, (value, width) in enumerate(zip(row_data, self.column_widths)):
            text = str(value) if value is not None else ""
            
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                font=(config.FONT_NAME, 12),
                text_color="black",
                width=width,
                anchor="center" if i in [0, 2, 3] else "w"
            )
            label.pack(side="left", padx=5, pady=8)

    def save_guest(self):
        """Save a new guest to the database."""
        name = self.get_input_text(self.name_entry)
        
        # Get raw text (might contain Khmer numerals)
        raw_khr = self.get_input_text(self.khr_entry)
        raw_usd = self.get_input_text(self.usd_entry)
        addr = self.get_input_text(self.addr_entry)
        
        # Debug Print
        print(f"Name: {name}, KHR: {raw_khr}, USD: {raw_usd}")

        # Convert Khmer numerals (១២៣) to Arabic (123)
        clean_khr = khmer_to_arabic(raw_khr)
        clean_usd = khmer_to_arabic(raw_usd)

        if not name:
            KhmerMessageBox.show_message(
                self, 
                "ការព្រមាន / Warning", 
                "សូមបញ្ចូលឈ្មោះភ្ញៀវ!\nPlease enter guest name!",
                "warning"
            )
            return

        try:
            khr = int(clean_khr) if clean_khr else 0
            usd = float(clean_usd) if clean_usd else 0.0
        except ValueError:
            KhmerMessageBox.show_message(
                self,
                "កំហុស / Error",
                "សូមបញ្ចូលចំនួនទឹកប្រាក់ឲ្យបានត្រឹមត្រូវ!\nPlease enter valid numbers only!",
                "error"
            )
            return

        self.db.add_guest(name, khr, usd, addr)
        self.clear_inputs()
        self.refresh_data()

    def clear_inputs(self):
        """Clear all input fields and focus on the name field."""
        self.clear_textbox(self.name_entry)
        self.clear_textbox(self.khr_entry)
        self.clear_textbox(self.usd_entry)
        self.clear_textbox(self.addr_entry)
        self.name_entry.focus()

    def refresh_data(self):
        """Refresh the data table and statistics display."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        rows = self.db.fetch_all()
        for index, row in enumerate(rows):
            formatted_row = (
                row[0],
                row[1],
                f"{row[2]:,}",
                f"{row[3]:,.2f}",
                row[4] if row[4] else ""
            )
            self.create_table_row(formatted_row, index)

        count, total_khr, total_usd = self.db.fetch_summary()
        summary_text = (
            f"សរុបភ្ញៀវ: {count or 0} នាក់   |   "
            f"ប្រាក់រៀល: {total_khr or 0:,.0f} ៛   |   "
            f"ប្រាក់ដុល្លារ: ${total_usd or 0:,.2f}"
        )
        self.stats_label.configure(text=summary_text)

    def export_excel(self):
        """Export guest data to Excel file with total sum."""
        try:
            conn = sqlite3.connect(config.DB_FILE)
            df = pd.read_sql_query("SELECT * FROM guests", conn)
            
            # Add a total row
            total_row = pd.DataFrame({
                'id': ['សរុប / TOTAL'],
                'name': [''],
                'khr': [df['khr'].sum()],
                'usd': [df['usd'].sum()],
                'address': ['']
            })
            
            # Concatenate the original data with the total row
            df_with_total = pd.concat([df, total_row], ignore_index=True)
            
            filename = "Wedding_List_Export.xlsx"
            df_with_total.to_excel(filename, index=False, engine='openpyxl')
            conn.close()
            KhmerMessageBox.show_message(
                self,
                "ជោគជ័យ / Success",
                f"ទិន្នន័យត្រូវបានរក្សាទុកក្នុង\nData saved in:\n{filename}",
                "info"
            )
        except Exception as e:
            KhmerMessageBox.show_message(
                self,
                "កំហុស / Error",
                f"ការនាំចេញបានបរាជ័យ\nExport failed:\n{str(e)}",
                "error"
            )
