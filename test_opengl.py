#!/usr/bin/env python3
"""
Simple test script to check if OpenGL and PySide6 are working correctly.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt
from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

class TestGLWidget(QOpenGLWidget):
    def initializeGL(self):
        print("OpenGL initialized successfully")
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        print("OpenGL paint successful")

class TestWindow:
    def __init__(self):
        print("TestWindow created successfully")

def main():
    print("Starting test application...")
    app = QApplication(sys.argv)
    print("QApplication created successfully")
    
    # Test creating a simple widget
    widget = TestGLWidget()
    print("TestGLWidget created successfully")
    
    # Test creating a window
    window = TestWindow()
    print("TestWindow created successfully")
    
    print("Test completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
