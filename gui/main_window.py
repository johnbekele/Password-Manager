import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from typing import List
from models.password_entry import PasswordEntry
from services.database_service import DatabaseService
from gui.entry_window import EntryWindow

class MainWindow:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.db_service = DatabaseService(master_password)
        self.entries = []
        self.filtered_entries = []
        
        self.window = tk.Tk()
        self.window.title("Secure Password Manager")
        self.window.geometry("1000x600")
        
        self._create_widgets()
        self._load_entries()
        self._center_window()
    
    def _center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"1000x600+{x}+{y}")
    
    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Add Entry", command=self._add_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Edit", command=self._edit_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Delete", command=self._delete_entry).pack(side=tk.LEFT, padx=(0, 15))
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(toolbar, text="Lock", command=self._lock_app).pack(side=tk.RIGHT)
        
        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=("website", "username", "email", "password", "notes"), show="headings")
        
        # Define columns
        self.tree.heading("website", text="Website/Service")
        self.tree.heading("username", text="Username")
        self.tree.heading("email", text="Email")
        self.tree.heading("password", text="Password")
        self.tree.heading("notes", text="Notes")
        
        # Configure column widths
        self.tree.column("website", width=200)
        self.tree.column("username", width=150)
        self.tree.column("email", width=200)
        self.tree.column("password", width=100)
        self.tree.column("notes", width=300)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context menu
        self.context_menu = tk.Menu(self.window, tearoff=0)
        self.context_menu.add_command(label="Copy Username", command=self._copy_username)
        self.context_menu.add_command(label="Copy Password", command=self._copy_password)
        self.context_menu.add_command(label="Copy Email", command=self._copy_email)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit", command=self._edit_entry)
        self.context_menu.add_command(label="Delete", command=self._delete_entry)
        
        self.tree.bind("<Button-3>", self._show_context_menu)  # Right click
        self.tree.bind("<Double-1>", self._edit_entry)  # Double click
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(status_frame, text="0 entries")
        self.count_label.pack(side=tk.RIGHT)
    
    def _load_entries(self):
        try:
            self.entries = self.db_service.get_all_entries()
            self.filtered_entries = self.entries.copy()
            self._refresh_tree()
            self._update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load entries: {str(e)}")
    
    def _refresh_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add entries
        for entry in self.filtered_entries:
            self.tree.insert("", tk.END, values=(
                entry.website,
                entry.username,
                entry.email,
                entry.masked_password,
                entry.notes[:50] + "..." if len(entry.notes) > 50 else entry.notes
            ), tags=(entry.id,))
    
    def _update_status(self):
        count = len(self.filtered_entries)
        self.count_label.config(text=f"{count} entries")
        self.status_label.config(text="Ready")
    
    def _on_search(self, *args):
        search_text = self.search_var.get().lower()
        if not search_text:
            self.filtered_entries = self.entries.copy()
        else:
            self.filtered_entries = [
                entry for entry in self.entries
                if (search_text in entry.website.lower() or
                    search_text in entry.username.lower() or
                    search_text in entry.email.lower())
            ]
        
        self._refresh_tree()
        self._update_status()
    
    def _get_selected_entry(self):
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        entry_id = int(item['tags'][0])
        
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def _add_entry(self):
        try:
            entry_window = EntryWindow(self.window)
            result = entry_window.show()
            
            if result:
                if self.db_service.save_entry(result):
                    self._load_entries()
                    self.status_label.config(text="Entry added successfully")
                else:
                    messagebox.showerror("Error", "Failed to save entry")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open entry window: {str(e)}")
        
    def _edit_entry(self, event=None):
        selected_entry = self._get_selected_entry()
        if not selected_entry:
            messagebox.showinfo("No Selection", "Please select an entry to edit.")
            return
        
        entry_window = EntryWindow(self.window, selected_entry)
        result = entry_window.show()
        
        if result:
            if self.db_service.save_entry(result):
                self._load_entries()
                self.status_label.config(text="Entry updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update entry")
        
    def _delete_entry(self):
        selected_entry = self._get_selected_entry()
        if not selected_entry:
            messagebox.showinfo("No Selection", "Please select an entry to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the entry for '{selected_entry.website}'?"):
            if self.db_service.delete_entry(selected_entry.id):
                self._load_entries()
                self.status_label.config(text="Entry deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete entry")
    
    def _copy_username(self):
        selected_entry = self._get_selected_entry()
        if selected_entry and selected_entry.username:
            pyperclip.copy(selected_entry.username)
            self.status_label.config(text="Username copied to clipboard")
    
    def _copy_password(self):
        selected_entry = self._get_selected_entry()
        if selected_entry and selected_entry.password:
            pyperclip.copy(selected_entry.password)
            self.status_label.config(text="Password copied to clipboard")
    
    def _copy_email(self):
        selected_entry = self._get_selected_entry()
        if selected_entry and selected_entry.email:
            pyperclip.copy(selected_entry.email)
            self.status_label.config(text="Email copied to clipboard")
    
    def _show_context_menu(self, event):
        if self.tree.identify_row(event.y):
            self.context_menu.post(event.x_root, event.y_root)
    
    def _lock_app(self):
        self.window.withdraw()
        from gui.login_window import LoginWindow
        login_window = LoginWindow()
        new_password = login_window.show()
        
        if new_password:
            self.master_password = new_password
            self.db_service = DatabaseService(new_password)
            self._load_entries()
            self.window.deiconify()
        else:
            self.window.quit()
    
    def run(self):
        self.window.mainloop()