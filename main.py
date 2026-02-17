import sqlite3
import os
import sys
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox, ttk
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
DB_FILE = os.getenv("DB_NAME", "wedding_data.db")
APP_TITLE = os.getenv("APP_TITLE", "Wedding Manager")
FONT_NAME = os.getenv("FONT_NAME", "Khmer OS Siemreap")
FONT_SIZE = int(os.getenv("FONT_SIZE", 12))

# --- DATABASE LAYER ---
class WeddingDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
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
        self.cursor.execute("INSERT INTO guests (name, khr, usd, address) VALUES (?, ?, ?, ?)", 
                           (name, khr, usd, address))
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT id, name, khr, usd, address FROM guests ORDER BY id DESC")
        return self.cursor.fetchall()

    def fetch_summary(self):
        self.cursor.execute("SELECT COUNT(id), SUM(khr), SUM(usd) FROM guests")
        return self.cursor.fetchone()

# --- UI LAYER ---
class WeddingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = WeddingDB()

        # Window Setup
        self.title(APP_TITLE)
        self.geometry("1200x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Fonts
        self.khmer_font = (FONT_NAME, FONT_SIZE)
        self.header_font = (FONT_NAME, 24, "bold")

        # Layout Grid (Left: Sidebar, Right: Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.refresh_data()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Title
        ctk.CTkLabel(self.sidebar, text="បញ្ចូលព័ត៌មាន", font=self.header_font).pack(pady=(30, 20))

        # Inputs
        self.name_entry = self.create_input("ឈ្មោះភ្ញៀវ (Name)")
        self.khr_entry = self.create_input("ប្រាក់រៀល (KHR)")
        self.usd_entry = self.create_input("ប្រាក់ដុល្លារ (USD)")
        self.addr_entry = self.create_input("អាសយដ្ឋាន (Address)")

        # Buttons
        save_btn = ctk.CTkButton(self.sidebar, text="រក្សាទុក (Save)", font=self.khmer_font, 
                                 height=45, fg_color="#2ecc71", hover_color="#27ae60", 
                                 command=self.save_guest)
        save_btn.pack(padx=20, pady=(20, 10), fill="x")

        export_btn = ctk.CTkButton(self.sidebar, text="ទាញយក Excel", font=self.khmer_font, 
                                   height=40, fg_color="#3498db", hover_color="#2980b9", 
                                   command=self.export_excel)
        export_btn.pack(padx=20, pady=5, fill="x")

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.sidebar, placeholder_text=placeholder, font=self.khmer_font, height=40)
        entry.pack(padx=20, pady=10, fill="x")
        return entry

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Summary Dashboard
        self.stats_label = ctk.CTkLabel(self.main_frame, text="", font=(FONT_NAME, 18, "bold"))
        self.stats_label.pack(pady=10)

        # --- THE FIX FOR "?? ??" FONT ISSUE ---
        style = ttk.Style()
        style.theme_use("clam")  # Crucial: 'clam' theme allows custom font rendering
        
        style.configure("Treeview", 
                        font=(FONT_NAME, 11), 
                        rowheight=40,   # Taller rows for Khmer vowels
                        background="white",
                        foreground="black")
        
        style.configure("Treeview.Heading", 
                        font=(FONT_NAME, 12, "bold"),
                        background="#e0e0e0")

        # Table
        columns = ("ID", "Name", "KHR", "USD", "Address")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # Define Headings
        headers = ["ល.រ", "ឈ្មោះ", "ប្រាក់រៀល", "ប្រាក់ដុល្លារ", "អាសយដ្ឋាន"]
        for col, title in zip(columns, headers):
            self.tree.heading(col, text=title)
            width = 60 if col == "ID" else 150
            self.tree.column(col, width=width, anchor="center" if col in ["ID", "KHR", "USD"] else "w")

        self.tree.pack(fill="both", expand=True)

    def save_guest(self):
        name = self.name_entry.get()
        khr_str = self.khr_entry.get()
        usd_str = self.usd_entry.get()
        addr = self.addr_entry.get()

        if not name:
            messagebox.showwarning("Warning", "សូមបញ្ចូលឈ្មោះភ្ញៀវ! (Name required)")
            return

        # Validation: Convert empty strings to 0
        try:
            khr = int(khr_str) if khr_str else 0
            usd = float(usd_str) if usd_str else 0.0
        except ValueError:
            messagebox.showerror("Error", "សូមបញ្ចូលចំនួនទឹកប្រាក់ឲ្យបានត្រឹមត្រូវ! (Numbers only)")
            return

        self.db.add_guest(name, khr, usd, addr)
        self.clear_inputs()
        self.refresh_data()

    def clear_inputs(self):
        self.name_entry.delete(0, "end")
        self.khr_entry.delete(0, "end")
        self.usd_entry.delete(0, "end")
        self.addr_entry.delete(0, "end")
        self.name_entry.focus()

    def refresh_data(self):
        # Clear Table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load Guests
        rows = self.db.fetch_all()
        for row in rows:
            # Format numbers with commas (e.g. 10,000)
            formatted_row = (row[0], row[1], f"{row[2]:,}", f"{row[3]:,.2f}", row[4])
            self.tree.insert("", "end", values=formatted_row)

        # Update Stats
        count, total_khr, total_usd = self.db.fetch_summary()
        summary_text = f"សរុបភ្ញៀវ: {count or 0} នាក់   |   ប្រាក់រៀល: {total_khr or 0:,.0f} ៛   |   ប្រាក់ដុល្លារ: ${total_usd or 0:,.2f}"
        self.stats_label.configure(text=summary_text)

    def export_excel(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            df = pd.read_sql_query("SELECT * FROM guests", conn)
            filename = "Wedding_List_Export.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"ទិន្នន័យត្រូវបានរក្សាទុកក្នុង \n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

if __name__ == "__main__":
    app = WeddingApp()
    app.mainloop()