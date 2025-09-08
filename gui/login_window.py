import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    def __init__(self):
        self.master_password = None
        self.window = tk.Tk()
        self.window.title("Password Manager - Login")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient()
        self.window.grab_set()
        
        self._create_widgets()
        self._center_window()
    
    def _center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (200 // 2)
        self.window.geometry(f"400x200+{x}+{y}")
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enter Master Password", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Password entry
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(password_frame, text="Master Password:").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        self.password_entry.bind('<Return>', lambda e: self._login())
        
        # Error label
        self.error_label = ttk.Label(main_frame, text="", foreground="red")
        self.error_label.pack(pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Login", command=self._login).pack(side=tk.RIGHT)
        
        # Focus on password entry
        self.password_entry.focus()
    
    def _login(self):
        password = self.password_entry.get()
        
        if not password:
            self.error_label.config(text="Please enter a master password.")
            return
        
        if len(password) < 6:
            self.error_label.config(text="Master password must be at least 6 characters long.")
            return
        
        self.master_password = password
        self.window.quit()
    
    def _cancel(self):
        self.window.quit()
    
    def show(self):
        self.window.mainloop()
        return self.master_password