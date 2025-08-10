#!/usr/bin/env python3
"""
Simple test version of Cubist app to debug issues.
"""

import sys
import os
from pathlib import Path

# Add the cubist package to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Starting imports...")
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt
    print("PySide6 imports OK")
    
    from cubist.ui.main_window import MainWindow
    print("MainWindow import OK")
    
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    app.setApplicationName("Cubist Test")
    print("QApplication created")
    
    print("Creating MainWindow...")
    main_window = MainWindow()
    print("MainWindow created")
    
    print("Showing window...")
    main_window.show()
    main_window.raise_()
    main_window.activateWindow()
    print("Window shown")
    
    print("Starting event loop...")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
