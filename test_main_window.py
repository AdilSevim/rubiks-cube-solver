#!/usr/bin/env python3
"""
Minimal test script to check if MainWindow can be created successfully.
"""

import sys
import os
from pathlib import Path

# Add the cubist package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from cubist.ui.main_window import MainWindow

def main():
    print("Starting minimal test application...")
    app = QApplication(sys.argv)
    print("QApplication created successfully")
    
    # Test creating the main window
    print("Creating MainWindow...")
    try:
        main_window = MainWindow()
        print("MainWindow created successfully")
        
        # Try to show the window
        print("Showing MainWindow...")
        main_window.show()
        print("MainWindow shown successfully")
        
        print("Test completed successfully")
        return 0
    except Exception as e:
        print(f"Error creating MainWindow: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
