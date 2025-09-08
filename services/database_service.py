import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from models.password_entry import PasswordEntry
from services.encryption_service import EncryptionService

class DatabaseService:
    def __init__(self, master_password: str):
        self.db_path = self._get_db_path()
        self.encryption_service = EncryptionService(master_password)
        self._initialize_database()
    
    def _get_db_path(self) -> str:
        app_data = os.path.expanduser("~")
        app_folder = os.path.join(app_data, "PasswordManager")
        os.makedirs(app_folder, exist_ok=True)
        return os.path.join(app_folder, "passwords.db")
    
    def _initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT NOT NULL,
                    username TEXT,
                    email TEXT,
                    password TEXT NOT NULL,
                    notes TEXT,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def get_all_entries(self) -> List[PasswordEntry]:
        entries = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, website, username, email, password, notes, 
                       date_created, date_modified 
                FROM password_entries 
                ORDER BY website
            ''')
            
            for row in cursor.fetchall():
                entry = PasswordEntry(
                    id=row[0],
                    website=row[1],
                    username=row[2] or "",
                    email=row[3] or "",
                    password=self.encryption_service.decrypt(row[4]),
                    notes=row[5] or "",
                    date_created=datetime.fromisoformat(row[6]) if row[6] else datetime.now(),
                    date_modified=datetime.fromisoformat(row[7]) if row[7] else datetime.now()
                )
                entries.append(entry)
        
        return entries
    
    def save_entry(self, entry: PasswordEntry) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                encrypted_password = self.encryption_service.encrypt(entry.password)
                
                if entry.id == 0:  # New entry
                    cursor.execute('''
                        INSERT INTO password_entries 
                        (website, username, email, password, notes, date_created, date_modified)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.website,
                        entry.username,
                        entry.email,
                        encrypted_password,
                        entry.notes,
                        entry.date_created.isoformat(),
                        entry.date_modified.isoformat()
                    ))
                else:  # Update existing
                    entry.date_modified = datetime.now()
                    cursor.execute('''
                        UPDATE password_entries 
                        SET website=?, username=?, email=?, password=?, notes=?, date_modified=?
                        WHERE id=?
                    ''', (
                        entry.website,
                        entry.username,
                        entry.email,
                        encrypted_password,
                        entry.notes,
                        entry.date_modified.isoformat(),
                        entry.id
                    ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving entry: {e}")
            return False
    
    def delete_entry(self, entry_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM password_entries WHERE id=?', (entry_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False