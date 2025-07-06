"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import sys
from PyQt6.QtWidgets import QApplication
from survey_gui import FarbenWolfGui


def main():
    """
    Starts the GUI application.

    Initializes the QApplication, shows the main window,
    and starts the event loop.
    """
    app = QApplication(sys.argv)
    window = FarbenWolfGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
