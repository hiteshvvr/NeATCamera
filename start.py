"""
PyQt6 Camera Application
------------------------
Initializes a Camera object and launches the StartWindow GUI.
"""

import sys
from PyQt6.QtWidgets import QApplication
from fcamera import Camera
from fprocess import StartWindow


def main() -> None:
    """Main entry point for the application."""
    # Initialize camera
    camera = Camera(0)
    camera.initialize()
    camera.get_frame()

    # Create Qt application
    app = QApplication(sys.argv)

    # Launch main window
    start_window = StartWindow(camera)
    start_window.show()

    # Run event loop
    exit_code = app.exec()
    camera.close_camera()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
