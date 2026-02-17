import sqlite3
import os
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox, ttk
from dotenv import load_dotenv # pip install python-dotenv

# Load configurations
load_dotenv()
DB_PATH = os.getenv("DB_NAME", "database.db")
APP_TITLE = os.getenv("WEDDING_NAME", "Wedding Guest List")
KHMER_FONT = (os.getenv("PRIMARY_FONT", "Khmer OS Siemreap"), 14)
KHMER_FONT_BOLD = (os.getenv("PRIMARY_FONT", "Khmer OS Siemreap"), 16, "bold")

class WeddingDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                khr INTEGER DEFAULT 0,
                usd REAL DEFAULT 0.0,
                address TEXT,
                note TEXT
            )
        ''')
        self.conn.commit()

    def add_guest(self, name, khr, usd, addr):
        self.cursor.execute("INSERT INTO guests (name, khr, usd, address) VALUES (?, ?, ?, ?)",
                           (name, khr, usd, addr))
        self.conn.commit()

    def get_guests(self):
        self.cursor.execute("SELECT id, name, khr, usd, address FROM guests ORDER BY id DESC")
        return self.cursor.fetchall()

class WeddingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = WeddingDB()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        
        # Configure Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (INPUT) ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="បញ្ចូលព័ត៌មានភ្ញៀវ", font=KHMER_FONT_BOLD).pack(pady=(30, 20))

        self.name_in = self.create_input("ឈ្មោះភ្ញៀវ (Name)")
        self.khr_in = self.create_input("ទឹកប្រាក់ជារៀល (KHR)")
        self.usd_in = self.create_input("ទឹកប្រាក់ជាដុល្លារ (USD)")
        self.addr_in = self.create_input("អាសយដ្ឋាន (Address)")

        self.save_btn = ctk.CTkButton(self.sidebar, text="រក្សាទុក (Save)", font=KHMER_FONT, 
                                     fg_color="#1a73e8", height=45, command=self.save)
        self.save_btn.pack(fill="x", padx=20, pady=20)

        self.export_btn = ctk.CTkButton(self.sidebar, text="ទាញយកជា Excel", font=KHMER_FONT,
                                       fg_color="#1e7e34", height=40, command=self.export)
        self.export_btn.pack(fill="x", padx=20, pady=5)

        # --- MAIN AREA ---
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Summary Header
        self.summary_card = ctk.CTkFrame(self.main_view, height=100)
        self.summary_card.pack(fill="x", pady=(0, 20))
        self.stats_text = ctk.CTkLabel(self.summary_card, text="", font=KHMER_FONT_BOLD)
        self.stats_text.pack(expand=True)

        # Table with Khmer Support
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Khmer OS Siemreap", 11), rowheight=35)
        self.style.configure("Treeview.Heading", font=("Khmer OS Siemreap", 12, "bold"))

        self.tree = ttk.Treeview(self.main_view, columns=("ID", "Name", "KHR", "USD", "Address"), show='headings')
        headings = {"ID": "ល.រ", "Name": "ឈ្មោះ", "KHR": "ប្រាក់រៀល", "USD": "ប្រាក់ដុល្លារ", "Address": "អាសយដ្ឋាន"}
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=120 if "ID" not in col else 50)
        
        self.tree.pack(fill="both", expand=True)
        self.refresh()

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.sidebar, placeholder_text=placeholder, font=KHMER_FONT, height=40)
        entry.pack(fill="x", padx=20, pady=10)
        return entry

    def save(self):
        try:
            name = self.name_in.get()
            khr = int(self.khr_in.get() or 0)
            usd = float(self.usd_in.get() or 0)
            addr = self.addr_in.get()

            if not name: 
                messagebox.showwarning("បញ្ជាក់", "សូមបញ្ចូលឈ្មោះភ្ញៀវ")
                return

            self.db.add_guest(name, khr, usd, addr)
            self.refresh()
            self.clear()
        except ValueError:
            messagebox.showerror("កំហុស", "សូមពិនិត្យមើលចំនួនទឹកប្រាក់")

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in self.db.get_guests(): self.tree.insert("", "end", values=row)
        
        # Calculate Totals
        self.db.cursor.execute("SELECT COUNT(id), SUM(khr), SUM(usd) FROM guests")
        c, k, u = self.db.cursor.fetchone()
        self.stats_text.configure(text=f"ភ្ញៀវសរុប: {c or 0} នាក់  |  សរុបប្រាក់រៀល: {k or 0:,.0f} ៛  |  សរុបប្រាក់ដុល្លារ: ${u or 0:,.2f}")

    def clear(self):
        for e in [self.name_in, self.khr_in, self.usd_in, self.addr_in]: e.delete(0, 'end')

    def export(self):
        df = pd.read_sql_query("SELECT * FROM guests", sqlite3.connect(DB_PATH))
        df.to_excel("របាយការណ៍អាពាហ៍ពិពាហ៍.xlsx", index=False)
        messagebox.showinfo("ជោគជ័យ", "ទាញយកទិន្នន័យបានជោគជ័យ!")

if __name__ == "__main__":
    app = WeddingApp()
    app.mainloop()