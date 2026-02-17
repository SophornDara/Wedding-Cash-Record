import sqlite3
import os
import sys
import io
import pandas as pd
import customtkinter as ctk
from tkinter import font as tkfont, Toplevel
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
DB_FILE = os.getenv("DB_NAME", "wedding_data.db")
APP_TITLE = os.getenv("APP_TITLE", "Wedding Manager")
FONT_SIZE = int(os.getenv("FONT_SIZE", 12))

# --- SYSTEM ENCODING FIX (CRITICAL FOR WINDOWS) ---
# Force Python to treat all output as UTF-8 to prevent "???" in terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# --- HELPER: CONVERT KHMER NUMBERS TO ARABIC ---
def khmer_to_arabic(text):
    """Converts Khmer numerals (១២៣) to standard numbers (123)"""
    if not text:
        return ""
    
    replacements = {
        '០': '0', '១': '1', '២': '2', '៣': '3', '៤': '4',
        '៥': '5', '៦': '6', '៧': '7', '៨': '8', '៩': '9',
        ',': '', ' ': ''  # Remove commas and spaces
    }
    
    text_str = str(text)
    for k, v in replacements.items():
        text_str = text_str.replace(k, v)
        
    return text_str

# --- FONT FINDER ---
def get_khmer_font():
    """Try to find an available Khmer font on the system"""
    try:
        # Priority list of fonts
        khmer_fonts = [
            "Khmer OS Siemreap",
            "Khmer OS Battambang", 
            "Khmer OS Content",
            "DaunPenh",  # Standard Windows font
            "Leelawadee UI", # Good fallback for Windows
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
    except:
        return "Arial"

FONT_NAME = get_khmer_font()
print(f"Using Font: {FONT_NAME}") # Debug print

# --- DATABASE LAYER ---
class WeddingDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        
        # FIX 1: Force SQLite to decode text as UTF-8
        self.conn.text_factory = lambda b: b.decode("utf-8", "ignore")
        
        self.cursor = self.conn.cursor()
        
        # FIX 2: Ensure DB file is UTF-8
        self.cursor.execute("PRAGMA encoding = 'UTF-8'")
        self.check_table()

    def check_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                khr INTEGER DEFAULT 0,
                usd REAL DEFAULT 0.0,
                address TEXT,
                note TEXT
            )
        """)
        self.conn.commit()

    def add_guest(self, name, khr, usd, address):
        # FIX 3: Explicitly cast to string/int/float before saving
        self.cursor.execute("INSERT INTO guests (name, khr, usd, address) VALUES (?, ?, ?, ?)", 
                           (str(name), int(khr), float(usd), str(address)))
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT id, name, khr, usd, address FROM guests ORDER BY id DESC")
        return self.cursor.fetchall()

    def fetch_summary(self):
        self.cursor.execute("SELECT COUNT(id), SUM(khr), SUM(usd) FROM guests")
        return self.cursor.fetchone()

# --- CUSTOM MESSAGE DIALOGS ---
class KhmerMessageBox:
    @staticmethod
    def show_message(parent, title, message, msg_type="info"):
        dialog = Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center
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
        
        btn_color = "#3498db" if msg_type == "info" else ("#e74c3c" if msg_type == "error" else "#f39c12")
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

# --- UI LAYER ---
class WeddingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = WeddingDB()

        self.title(APP_TITLE)
        self.geometry("1200x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Fonts
        self.khmer_font = (FONT_NAME, FONT_SIZE)
        self.header_font = (FONT_NAME, 24, "bold")
        
        # Global Font Setting for CTk
        # This helps apply the font to all widgets generally
        try:
            ctk.FontManager.load_font(FONT_NAME)
        except:
            pass 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.refresh_data()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="បញ្ចូលព័ត៌មាន", font=self.header_font).pack(pady=(30, 20))

        self.name_entry = self.create_input("ឈ្មោះភ្ញៀវ (Name)")
        self.khr_entry = self.create_input("ប្រាក់រៀល (KHR)")
        self.usd_entry = self.create_input("ប្រាក់ដុល្លារ (USD)")
        self.addr_entry = self.create_input("អាសយដ្ឋាន (Address)")

        save_btn = ctk.CTkButton(self.sidebar, text="រក្សាទុក (Save)", font=self.khmer_font, 
                                 height=45, fg_color="#2ecc71", hover_color="#27ae60", 
                                 command=self.save_guest)
        save_btn.pack(padx=20, pady=(20, 10), fill="x")

        export_btn = ctk.CTkButton(self.sidebar, text="ទាញយក Excel", font=self.khmer_font, 
                                   height=40, fg_color="#3498db", hover_color="#2980b9", 
                                   command=self.export_excel)
        export_btn.pack(padx=20, pady=5, fill="x")

    def create_input(self, placeholder):
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(padx=20, pady=5, fill="x")
        
        label = ctk.CTkLabel(frame, text=placeholder, font=(FONT_NAME, 11), 
                             text_color="gray60", anchor="w")
        label.pack(fill="x")
        
        # FIX: Explicit Font Object for Input
        # This fixes the "???" issue in the input box
        input_font = ctk.CTkFont(family=FONT_NAME, size=FONT_SIZE)
        
        textbox = ctk.CTkTextbox(frame, font=input_font, height=40, 
                                 wrap="none", activate_scrollbars=False)
        textbox.pack(fill="x", pady=(2, 5))
        
        textbox.bind("<Return>", lambda e: "break")
        
        return textbox
    
    def get_input_text(self, textbox):
        return textbox.get("1.0", "end-1c").strip()
    
    def clear_textbox(self, textbox):
        textbox.delete("1.0", "end")

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.stats_label = ctk.CTkLabel(
            self.main_frame, 
            text="", 
            font=(FONT_NAME, 18, "bold")
        )
        self.stats_label.pack(pady=10)

        # Header Frame
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="#e0e0e0", height=45)
        header_frame.pack(fill="x", pady=(10, 0))
        header_frame.pack_propagate(False)
        
        headers = ["ល.រ", "ឈ្មោះ", "ប្រាក់រៀល", "ប្រាក់ដុល្លារ", "អាសយដ្ឋាន"]
        widths = [60, 200, 150, 150, 200]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                header_frame, 
                text=header, 
                font=(FONT_NAME, 13, "bold"),
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
        bg_color = "#f8f9fa" if row_index % 2 == 0 else "white"
        
        row_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color, height=45)
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)
        
        for i, (value, width) in enumerate(zip(row_data, self.column_widths)):
            text = str(value) if value is not None else ""
            
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                font=(FONT_NAME, 12),
                text_color="black",
                width=width,
                anchor="center" if i in [0, 2, 3] else "w"
            )
            label.pack(side="left", padx=5, pady=8)

    def save_guest(self):
        name = self.get_input_text(self.name_entry)
        
        # Get raw text (might contain Khmer numerals)
        raw_khr = self.get_input_text(self.khr_entry)
        raw_usd = self.get_input_text(self.usd_entry)
        addr = self.get_input_text(self.addr_entry)
        
        # Debug Print
        print(f"Name: {name}, KHR: {raw_khr}, USD: {raw_usd}")

        # FIX: Convert Khmer numerals (១២៣) to Arabic (123)
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
        self.clear_textbox(self.name_entry)
        self.clear_textbox(self.khr_entry)
        self.clear_textbox(self.usd_entry)
        self.clear_textbox(self.addr_entry)
        self.name_entry.focus()

    def refresh_data(self):
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
        summary_text = f"សរុបភ្ញៀវ: {count or 0} នាក់   |   ប្រាក់រៀល: {total_khr or 0:,.0f} ៛   |   ប្រាក់ដុល្លារ: ${total_usd or 0:,.2f}"
        self.stats_label.configure(text=summary_text)

    def export_excel(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            df = pd.read_sql_query("SELECT * FROM guests", conn)
            filename = "Wedding_List_Export.xlsx"
            df.to_excel(filename, index=False, engine='openpyxl')
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

if __name__ == "__main__":
    app = WeddingApp()
    app.mainloop()