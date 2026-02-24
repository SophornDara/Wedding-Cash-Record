"""Wedding database operations and management."""

import sqlite3
from config import DB_FILE


class WeddingDB:
    """Database handler for wedding guest management."""
    
    def __init__(self):
        """Initialize database connection and setup tables."""
        self.conn = sqlite3.connect(DB_FILE)
        
        # FIX 1: Force SQLite to decode text as UTF-8
        self.conn.text_factory = lambda b: b.decode("utf-8", "ignore")
        
        self.cursor = self.conn.cursor()
        
        # FIX 2: Ensure DB file is UTF-8
        self.cursor.execute("PRAGMA encoding = 'UTF-8'")
        self.check_table()

    def check_table(self):
        """Create guests table if it doesn't exist."""
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
        """Add a new guest to the database.
        
        Args:
            name (str): Guest name
            khr (int): Amount in Khmer Riel
            usd (float): Amount in US Dollars
            address (str): Guest address
        """
        # FIX 3: Explicitly cast to string/int/float before saving
        self.cursor.execute(
            "INSERT INTO guests (name, khr, usd, address) VALUES (?, ?, ?, ?)", 
            (str(name), int(khr), float(usd), str(address))
        )
        self.conn.commit()

    def fetch_all(self):
        """Fetch all guests ordered by ID descending.
        
        Returns:
            list: List of guest records (id, name, khr, usd, address)
        """
        self.cursor.execute("SELECT id, name, khr, usd, address FROM guests ORDER BY id DESC")
        return self.cursor.fetchall()

    def fetch_summary(self):
        """Fetch summary statistics.
        
        Returns:
            tuple: (count, total_khr, total_usd)
        """
        self.cursor.execute("SELECT COUNT(id), SUM(khr), SUM(usd) FROM guests")
        return self.cursor.fetchone()

    def get_guest_by_id(self, guest_id):
        """Get a single guest by ID.
        
        Args:
            guest_id (int): The guest's database ID
            
        Returns:
            tuple: Guest record (id, name, khr, usd, address) or None
        """
        self.cursor.execute("SELECT id, name, khr, usd, address FROM guests WHERE id = ?", (guest_id,))
        return self.cursor.fetchone()

    def update_guest(self, guest_id, name, khr, usd, address):
        """Update an existing guest in the database.
        
        Args:
            guest_id (int): The guest's database ID
            name (str): Guest name
            khr (int): Amount in Khmer Riel
            usd (float): Amount in US Dollars
            address (str): Guest address
        """
        self.cursor.execute(
            "UPDATE guests SET name = ?, khr = ?, usd = ?, address = ? WHERE id = ?",
            (str(name), int(khr), float(usd), str(address), guest_id)
        )
        self.conn.commit()

    def delete_guest(self, guest_id):
        """Delete a guest from the database.
        
        Args:
            guest_id (int): The guest's database ID
        """
        self.cursor.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()
