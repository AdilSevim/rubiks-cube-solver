#!/usr/bin/env python3
"""
Cubist - 3×3 Rubik's Cube Solver & Tutor
Main application entry point.
"""

import sys
import os
from pathlib import Path

# Add the cubist package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QIcon

from cubist.ui.main_window import MainWindow


def show_splash_screen(app: QApplication) -> QSplashScreen:
    """Show splash screen during startup."""
    # Create a simple splash screen
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(Qt.white)
    
    splash = QSplashScreen(splash_pixmap)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
    
    # Add text to splash screen
    splash.showMessage(
        "Cubist - 3×3 Rubik's Cube Solver & Tutor\n\nLoading...",
        Qt.AlignCenter | Qt.AlignBottom,
        Qt.black
    )
    
    splash.show()
    app.processEvents()
    
    return splash


def check_dependencies() -> bool:
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import PySide6
    except ImportError:
        missing_deps.append("PySide6")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import kociemba
    except ImportError:
        missing_deps.append("kociemba")
    
    try:
        import reportlab
    except ImportError:
        missing_deps.append("reportlab")
    
    try:
        from OpenGL import GL
    except ImportError:
        missing_deps.append("PyOpenGL")
    
    if missing_deps:
        QMessageBox.critical(
            None,
            "Missing Dependencies",
            f"The following required packages are missing:\n\n" +
            "\n".join(f"• {dep}" for dep in missing_deps) +
            f"\n\nPlease install them using:\n" +
            f"pip install {' '.join(missing_deps)}"
        )
        return False
    
    return True


def setup_application() -> QApplication:
    """Set up the QApplication with proper settings."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Cubist")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Cubist Development Team")
    app.setApplicationDisplayName("Cubist - 3×3 Rubik's Cube Solver & Tutor")
    
    # Set application icon (if available)
    icon_path = Path(__file__).parent / "cubist" / "assets" / "icons" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def main() -> int:
    """Main application entry point."""
    try:
        # Create application
        app = setup_application()
        
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Show splash screen
        splash = show_splash_screen(app)
        
        # Create main window
        main_window = MainWindow()
        
        # Close splash screen after a short delay
        def close_splash():
            splash.finish(main_window)
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
        
        QTimer.singleShot(2000, close_splash)  # 2 second delay
        
        # Run application
        return app.exec()
        
    except Exception as e:
        # Handle any startup errors
        error_msg = f"Failed to start Cubist:\n\n{str(e)}"
        
        try:
            QMessageBox.critical(None, "Startup Error", error_msg)
        except:
            # If Qt is not available, print to console
            print(f"ERROR: {error_msg}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
