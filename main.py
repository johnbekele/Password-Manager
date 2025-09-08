#!/usr/bin/env python3
"""
Secure Password Manager
A simple, secure password manager built with Python and Tkinter
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.login_window import LoginWindow
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        # Show login window
        login_window = LoginWindow()
        master_password = login_window.show()
        
        if not master_password:
            print("Login cancelled. Exiting...")
            return
        
        # Show main application window
        app = MainWindow(master_password)
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()