"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import os

from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout, QLabel, QApplication)

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QIcon

from config import FWConfig
from settings_tab import SettingsTab
from survey_tab import SurveyTab
from utils import resource_path


class FarbenWolfGui(QWidget):
    """
    Main GUI class for the FarbenWolf application.

    Provides the user interface for managing customer data, 
    creating surveys/documents, and visualizing shapes.

    Inherits from:
        QWidget: Base class for all UI objects in PyQt/PySide.
    """

    def __init__(self):
        super().__init__()
        self.config = FWConfig()

        # set primaryScreen max Windowmode
        screen = QApplication.primaryScreen()
        geometry: QRect = screen.availableGeometry()
        self.setGeometry(geometry)
        self.showMaximized()

        self.base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), ".."))

        # Set window icon
        icon_path = resource_path(
            "resources/LogoIcon.png", self.base_dir)
        self.setWindowIcon(QIcon(icon_path))

        # Display logo at the top
        logo_label = QLabel()
        logo_path = resource_path(os.path.join(
            "resources", "LogoTransparent.png"), self.base_dir)
        logo_pixmap = QPixmap(logo_path)
        logo_label.setPixmap(logo_pixmap.scaledToHeight(
            60, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Initialize tabs
        self.tabs = QTabWidget()
        self.tab_aufmass = QWidget()
        self.tab_settings = QWidget()

        # Main layout with logo at the top center
        main_layout = QVBoxLayout()
        main_layout.addWidget(logo_label)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Load and apply QSS stylesheet
        style_path = resource_path(os.path.join(
            "resources", "style.qss"), self.base_dir)
        self.setStyleSheet(self._load_stylesheet(style_path))

        self._init_tab_aufmass()
        self._init_tab_settings()

    def closeEvent(self, event):
        """
        Handles the window close event.

        Checks if the survey tab needs saving before closing.
        Prevents closing if the user cancels the save action.
        """
        if hasattr(self, "tab_survey"):
            if not self.tab_survey.check_save_before_action():
                event.ignore()
                return
            self.tab_survey.close_plotter()
        event.accept()

    def _init_tab_aufmass(self):
        """Initialize the 'Survey' tab and add it to the tab view."""
        self.tab_survey = SurveyTab(self.config)
        self.tabs.addTab(self.tab_survey, "Aufmaß")

    def _init_tab_settings(self):
        """Initialize the 'Settings' tab and add it to the tab view."""
        self.tab_settings = SettingsTab(self.config)
        self.tabs.addTab(self.tab_settings, "Einstellungen")

    def _load_stylesheet(self, path: str) -> str:
        """Loads and returns a QSS stylesheet from a given file path."""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
