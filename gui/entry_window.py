import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
from models.password_entry import PasswordEntry

class EntryWindow:
    def __init__(self, parent, entry=None):
        self.parent = parent
        self.entry = entry if entry else PasswordEntry()
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Add Entry" if not entry else "Edit Entry")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        
        # Try to set grab, but handle gracefully if it fails
        try:
            self.window.grab_set()
        except tk.TclError:
            # If grab fails, just continue without it
            pass
        
        self._create_widgets()
        self._center_window()
        
        if entry:
            self._load_entry_data()
        
        # Alternative way to make window modal
        self.window.focus_set()
        self.window.lift()
    
    def _center_window(self):
        self.window.update_idletasks()
        try:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (500 // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (400 // 2)
            self.window.geometry(f"500x400+{x}+{y}")
        except tk.TclError:
            # If parent window info is not available, center on screen
            self.window.update_idletasks()
            x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.window.winfo_screenheight() // 2) - (400 // 2)
            self.window.geometry(f"500x400+{x}+{y}")
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Website
        ttk.Label(main_frame, text="Website/Service:*").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.website_entry = ttk.Entry(main_frame, width=50)
        self.website_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame, width=50)
        self.username_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.email_entry = ttk.Entry(main_frame, width=50)
        self.email_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:*").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(main_frame, width=40)
        self.password_entry.grid(row=3, column=1, sticky=tk.W+tk.E, pady=(0, 10))
        
        generate_btn = ttk.Button(main_frame, text="Generate", command=self._generate_password)
        generate_btn.grid(row=3, column=2, padx=(5, 0), pady=(0, 10))
        
        # Notes
        ttk.Label(main_frame, text="Notes:").grid(row=4, column=0, sticky=tk.W+tk.N, pady=(0, 5))
        self.notes_text = tk.Text(main_frame, width=50, height=6)
        self.notes_text.grid(row=4, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E)
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self._save).pack(side=tk.RIGHT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Focus on first field
        self.website_entry.focus()
        
        # Bind escape key to cancel
        self.window.bind('<Escape>', lambda e: self._cancel())
        
        # Handle window close button
        self.window.protocol("WM_DELETE_WINDOW", self._cancel)
    
    def _load_entry_data(self):
        self.website_entry.insert(0, self.entry.website)
        self.username_entry.insert(0, self.entry.username)
        self.email_entry.insert(0, self.entry.email)
        self.password_entry.insert(0, self.entry.password)
        self.notes_text.insert(tk.END, self.entry.notes)
    
    def _generate_password(self):
        # Generate secure password
        length = 16
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
    
    def _save(self):
        website = self.website_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not website:
            messagebox.showerror("Validation Error", "Website/Service field is required.")
            self.website_entry.focus()
            return
        
        if not password:
            messagebox.showerror("Validation Error", "Password field is required.")
            self.password_entry.focus()
            return
        
        self.entry.website = website
        self.entry.username = self.username_entry.get().strip()
        self.entry.email = self.email_entry.get().strip()
        self.entry.password = password
        self.entry.notes = self.notes_text.get(1.0, tk.END).strip()
        
        self.result = self.entry
        self._close_window()
    
    def _cancel(self):
        self.result = None
        self._close_window()
    
    def _close_window(self):
        try:
            self.window.grab_release()
        except tk.TclError:
            pass
        self.window.destroy()
    
    def show(self):
        # Wait for the window to be destroyed
        self.parent.wait_window(self.window)
        return self.result