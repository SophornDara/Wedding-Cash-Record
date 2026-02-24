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
        self.editing_id = None  # Track which guest is being edited

        self.title(config.APP_TITLE)
        self.geometry("1400x800")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fonts - use config module for dynamic font detection
        self.khmer_font = (config.FONT_NAME, config.FONT_SIZE)
        self.header_font = (config.FONT_NAME, 26, "bold")
        self.title_font = (config.FONT_NAME, 20, "bold")
        self.stat_font = (config.FONT_NAME, 24, "bold")
        
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
        self.sidebar = ctk.CTkFrame(self, width=360, corner_radius=0, fg_color="#f8f9fa")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Header with background
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="#1e88e5", corner_radius=0)
        header_frame.pack(fill="x", pady=0)
        
        ctk.CTkLabel(
            header_frame, 
            text="បញ្ចូលព័ត៌មាន", 
            font=self.header_font,
            text_color="white"
        ).pack(pady=25)

        # Form container
        form_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.name_entry = self.create_input(form_frame, "ឈ្មោះភ្ញៀវ (Name)")
        self.khr_entry = self.create_input(form_frame, "ប្រាក់រៀល (KHR៛)")
        self.usd_entry = self.create_input(form_frame, "ប្រាក់ដុល្លារ (USD $)")
        self.addr_entry = self.create_input(form_frame, "អាសយដ្ឋាន (Address)")

        # Button container
        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.save_btn = ctk.CTkButton(
            btn_frame, 
            text="✓ រក្សាទុក (Save)", 
            font=self.khmer_font, 
            height=50, 
            fg_color="#10b981", 
            hover_color="#059669",
            corner_radius=8,
            command=self.save_guest
        )
        self.save_btn.pack(fill="x", pady=5)

        self.cancel_btn = ctk.CTkButton(
            btn_frame, 
            text="✕ បោះបង់ (Cancel)", 
            font=self.khmer_font, 
            height=45, 
            fg_color="#6b7280", 
            hover_color="#4b5563",
            corner_radius=8,
            command=self.cancel_edit
        )
        self.cancel_btn.pack(fill="x", pady=5)
        self.cancel_btn.pack_forget()  # Hide initially

        export_btn = ctk.CTkButton(
            btn_frame, 
            text="📊 ទាញយក Excel", 
            font=self.khmer_font, 
            height=45, 
            fg_color="#3b82f6", 
            hover_color="#2563eb",
            corner_radius=8,
            command=self.export_excel
        )
        export_btn.pack(fill="x", pady=5)

    def create_input(self, parent, placeholder):
        """Create an input field with label using native tkinter Text widget.
        
        Args:
            parent: Parent widget
            placeholder (str): Label text for the input field
            
        Returns:
            tk.Text: The created text input widget
        """
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(padx=0, pady=8, fill="x")
        
        label = ctk.CTkLabel(
            frame, 
            text=placeholder, 
            font=(config.FONT_NAME, 12, "bold"), 
            text_color="#374151", 
            anchor="w"
        )
        label.pack(fill="x", pady=(0, 5))
        
        # Use native tkinter Text widget for proper Khmer support
        textbox = tk.Text(
            frame,
            font=(config.FONT_NAME, config.FONT_SIZE),
            height=2,
            width=30,
            wrap="none",
            bg="white",
            fg="#1f2937",
            insertbackground="#1e88e5",
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=10
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
        self.main_frame = ctk.CTkFrame(self, fg_color="#ffffff")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title bar
        title_bar = ctk.CTkFrame(self.main_frame, fg_color="#1e88e5", height=70, corner_radius=0)
        title_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        title_bar.grid_propagate(False)
        
        ctk.CTkLabel(
            title_bar, 
            text="📋 ទិន្នន័យភ្ញៀវ / Guest Management", 
            font=self.title_font,
            text_color="white"
        ).pack(side="left", padx=30, pady=20)

        # Statistics cards container
        stats_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        stats_container.grid(row=1, column=0, sticky="ew", padx=30, pady=(20, 10))
        stats_container.grid_columnconfigure((0, 1, 2), weight=1)

        # Total Guests Card
        self.guests_card = self.create_stat_card(
            stats_container, 
            "សរុបភ្ញៀវ\nTotal Guests", 
            "0",
            "#8b5cf6",
            0
        )
        
        # Total KHR Card
        self.khr_card = self.create_stat_card(
            stats_container, 
            "សរុបរៀល\nTotal KHR", 
            "0 ៛",
            "#10b981",
            1
        )
        
        # Total USD Card
        self.usd_card = self.create_stat_card(
            stats_container, 
            "សរុបដុល្លារ\nTotal USD", 
            "$0.00",
            "#f59e0b",
            2
        )

        # Search bar
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 5))
        
        ctk.CTkLabel(
            search_frame, 
            text="🔍", 
            font=(config.FONT_NAME, 16)
        ).pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="ស្វែងរកតាមឈ្មោះ... Search by name...",
            font=self.khmer_font,
            height=40,
            border_width=2,
            corner_radius=8
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Table container
        table_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        table_container.grid(row=3, column=0, sticky="nsew", padx=30, pady=(5, 20))
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Header Frame
        header_frame = ctk.CTkFrame(table_container, fg_color="#e5e7eb", height=50, corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        header_frame.grid_propagate(False)
        
        headers = ["ល.រ", "ឈ្មោះ / Name", "រៀល / KHR", "ដុល្លារ / USD", "អាសយដ្ឋាន / Address", "សកម្មភាព"]
        widths = [60, 220, 140, 140, 240, 160]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                header_frame, 
                text=header, 
                font=(config.FONT_NAME, 13, "bold"),
                text_color="#1f2937",
                width=width
            )
            label.pack(side="left", padx=8, pady=12)
        
        self.table_frame = ctk.CTkScrollableFrame(
            table_container, 
            fg_color="#f9fafb",
            corner_radius=8,
            scrollbar_button_color="#3b82f6",
            scrollbar_button_hover_color="#2563eb"
        )
        self.table_frame.grid(row=1, column=0, sticky="nsew")
        
        self.column_widths = widths

    def create_stat_card(self, parent, title, value, color, column):
        """Create a statistics card.
        
        Args:
            parent: Parent widget
            title (str): Card title
            value (str): Card value
            color (str): Card accent color
            column (int): Grid column position
            
        Returns:
            ctk.CTkLabel: The value label for updating
        """
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=2, border_color="#e5e7eb")
        card.grid(row=0, column=column, padx=10, pady=0, sticky="ew")
        
        # Color accent bar
        accent = ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0)
        accent.pack(fill="x", pady=0)
        
        # Card content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=(config.FONT_NAME, 11),
            text_color="#6b7280",
            justify="center"
        )
        title_label.pack(pady=(0, 8))
        
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=self.stat_font,
            text_color="#1f2937"
        )
        value_label.pack()
        
        return value_label

    def create_table_row(self, row_data, row_index, guest_id):
        """Create a row in the data table.
        
        Args:
            row_data (tuple): Data for the row
            row_index (int): Index of the row for alternating colors
            guest_id (int): Database ID of the guest
        """
        bg_color = "white" if row_index % 2 == 0 else "#f3f4f6"
        
        row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color, height=55, corner_radius=6)
        row_frame.pack(fill="x", pady=2, padx=5)
        row_frame.pack_propagate(False)
        
        # Data columns
        for i, (value, width) in enumerate(zip(row_data, self.column_widths[:-1])):
            text = str(value) if value is not None else ""
            
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                font=(config.FONT_NAME, 12),
                text_color="#1f2937",
                width=width,
                anchor="center" if i in [0, 2, 3] else "w"
            )
            label.pack(side="left", padx=8, pady=8)

        # Action buttons
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=self.column_widths[-1])
        action_frame.pack(side="left", padx=8)
        action_frame.pack_propagate(False)
        
        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ កែ",
            font=(config.FONT_NAME, 11),
            width=65,
            height=32,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            corner_radius=6,
            command=lambda: self.edit_guest(guest_id)
        )
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ លុប",
            font=(config.FONT_NAME, 11),
            width=65,
            height=32,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=6,
            command=lambda: self.delete_guest(guest_id)
        )
        delete_btn.pack(side="left", padx=2)

    def save_guest(self):
        """Save a new guest or update existing guest in the database."""
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

        if self.editing_id:
            # Update existing guest
            self.db.update_guest(self.editing_id, name, khr, usd, addr)
            self.editing_id = None
            self.save_btn.configure(text="✓ រក្សាទុក (Save)")
            self.cancel_btn.pack_forget()
        else:
            # Add new guest
            self.db.add_guest(name, khr, usd, addr)
            
        self.clear_inputs()
        self.refresh_data()

    def cancel_edit(self):
        """Cancel editing mode and clear form."""
        self.editing_id = None
        self.save_btn.configure(text="✓ រក្សាទុក (Save)")
        self.cancel_btn.pack_forget()
        self.clear_inputs()

    def edit_guest(self, guest_id):
        """Load guest data into form for editing.
        
        Args:
            guest_id (int): Database ID of the guest to edit
        """
        guest = self.db.get_guest_by_id(guest_id)
        if guest:
            self.editing_id = guest_id
            
            # Clear and populate fields
            self.clear_textbox(self.name_entry)
            self.name_entry.insert("1.0", guest[1])
            
            self.clear_textbox(self.khr_entry)
            self.khr_entry.insert("1.0", str(guest[2]))
            
            self.clear_textbox(self.usd_entry)
            self.usd_entry.insert("1.0", str(guest[3]))
            
            self.clear_textbox(self.addr_entry)
            if guest[4]:
                self.addr_entry.insert("1.0", guest[4])
            
            # Update UI for edit mode
            self.save_btn.configure(text="💾 ធ្វើបច្ចុប្បន្នភាព (Update)")
            self.cancel_btn.pack(fill="x", pady=5)
            self.name_entry.focus()

    def delete_guest(self, guest_id):
        """Delete a guest from the database.
        
        Args:
            guest_id (int): Database ID of the guest to delete
        """
        result = KhmerMessageBox.show_confirm(
            self,
            "បញ្ជាក់ / Confirm",
            "តើអ្នកប្រាកដថាចង់លុបភ្ញៀវនេះទេ?\nAre you sure you want to delete this guest?"
        )
        
        if result:
            self.db.delete_guest(guest_id)
            if self.editing_id == guest_id:
                self.cancel_edit()
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
        
        # Get search query
        search_query = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""
        
        # Fetch and filter data
        rows = self.db.fetch_all()
        if search_query:
            rows = [row for row in rows if search_query.lower() in row[1].lower()]
        
        # Display filtered rows
        for index, row in enumerate(rows):
            formatted_row = (
                row[0],
                row[1],
                f"{row[2]:,}",
                f"{row[3]:,.2f}",
                row[4] if row[4] else ""
            )
            self.create_table_row(formatted_row, index, row[0])

        # Update statistics (always show all data, not filtered)
        count, total_khr, total_usd = self.db.fetch_summary()
        
        # Update stat cards
        if hasattr(self, 'guests_card'):
            self.guests_card.configure(text=f"{count or 0} នាក់")
            self.khr_card.configure(text=f"{total_khr or 0:,.0f} ៛")
            self.usd_card.configure(text=f"${total_usd or 0:,.2f}")

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
