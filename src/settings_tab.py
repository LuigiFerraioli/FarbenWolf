"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QComboBox,
    QFileDialog, QMessageBox, QCheckBox
)

from PyQt6.QtGui import QIcon


class SettingsTab(QWidget):
    """
    A QWidget subclass representing the Settings tab UI,
    including controls for storage location, job list management,
    output format and unit selection, and saving settings.

    Args:
        config: A configuration object that must have `get` and `update` methods.
        parent: Optional parent widget.
    """

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Speicherort
        h_speicherort = QHBoxLayout()
        h_speicherort.addWidget(QLabel("Speicherort"))
        self.edit_speicherort = QLineEdit()
        self.edit_speicherort.setText(self.config.get(
            "Speicherort", str(Path.home() / "Desktop")))
        h_speicherort.addWidget(self.edit_speicherort)
        btn_browse = QPushButton("...")
        btn_browse.clicked.connect(self._browse_speicherort)
        h_speicherort.addWidget(btn_browse)
        layout.addLayout(h_speicherort)
        layout.addSpacing(20)

        # Dateinamensbestandteile
        layout.addWidget(QLabel("Dateinamensbestandteile"))
        self.dateiname_combo = QComboBox()
        options = ["Keine", "Name", "Datum", "Uhrzeit", "Name + Datum",
                   "Name + Uhrzeit", "Datum + Uhrzeit", "Name + Datum + Uhrzeit"]
        self.dateiname_combo.addItems(options)
        self._set_dateiname_combo_from_config(self.config)
        layout.addWidget(self.dateiname_combo)
        layout.addSpacing(20)

        # Arbeiten
        layout.addWidget(QLabel("Arbeiten (bearbeiten)"))
        self.list_arbeiten = QListWidget()
        self._load_arbeiten()
        layout.addWidget(self.list_arbeiten)
        layout.addSpacing(20)

        h_arbeit_add = QHBoxLayout()
        self.edit_neue_arbeit = QLineEdit()
        self.edit_neue_arbeit.setPlaceholderText("Neue Arbeit hinzufügen")
        btn_arbeit_add = QPushButton()
        btn_arbeit_add.setIcon(QIcon.fromTheme("list-add"))
        btn_arbeit_add.setToolTip("Hinzufügen")
        btn_arbeit_add.setFixedWidth(100)
        btn_arbeit_add.clicked.connect(self._add_arbeit)
        h_arbeit_add.addWidget(self.edit_neue_arbeit)
        h_arbeit_add.addWidget(btn_arbeit_add)
        h_arbeit_add.addSpacing(20)
        layout.addLayout(h_arbeit_add)
        layout.addSpacing(20)

        # Ausgabedokument
        h_ausgabe = QHBoxLayout()
        label_ausgabe = QLabel("Ausgabedokument")
        label_ausgabe.setFixedWidth(200)
        h_ausgabe.addWidget(label_ausgabe)
        self.combo_ausgabe = QComboBox()
        self.combo_ausgabe.setFixedWidth(200)
        self.combo_ausgabe.addItems(["pdf", "excel", "pdf & excel"])
        self.combo_ausgabe.setCurrentText(
            self.config.get("Ausgabedokument", "pdf"))
        h_ausgabe.addWidget(self.combo_ausgabe)
        h_ausgabe.addStretch()
        layout.addLayout(h_ausgabe)
        layout.addSpacing(10)

        # Einheit
        h_einheit = QHBoxLayout()
        label_einheit = QLabel("Einheit")
        label_einheit.setFixedWidth(200)
        h_einheit.addWidget(label_einheit)
        self.combo_einheit = QComboBox()
        self.combo_einheit.setFixedWidth(200)
        self.combo_einheit.addItems(["m", "cm", "mm"])
        self.combo_einheit.setCurrentText(self.config.get("Einheit", "m"))
        h_einheit.addWidget(self.combo_einheit)
        h_einheit.addStretch()
        layout.addLayout(h_einheit)
        layout.addSpacing(10)

        # PDF automatisch öffnen
        h_pdf_auto = QHBoxLayout()
        label_pdf_auto = QLabel("PDF automatisch öffnen")
        label_pdf_auto.setFixedWidth(200)
        h_pdf_auto.addWidget(label_pdf_auto)
        self.btn_pdf_auto = QPushButton("✓" if self.config.get(
            "PDF automatisch öffnen", True) else "✗")
        self.btn_pdf_auto.setCheckable(True)
        self.btn_pdf_auto.setChecked(
            self.config.get("PDF automatisch öffnen", True))
        self.btn_pdf_auto.setFixedWidth(200)
        self.btn_pdf_auto.toggled.connect(
            lambda checked: self.btn_pdf_auto.setText("✓" if checked else "✗"))
        h_pdf_auto.addWidget(self.btn_pdf_auto)
        h_pdf_auto.addStretch()
        layout.addLayout(h_pdf_auto)
        layout.addSpacing(20)

        # Buttons
        btn_save = QPushButton("Speichern")
        btn_save.setFixedWidth(200)
        btn_save.clicked.connect(lambda: self._save_settings(True))
        btn_reset = QPushButton("Reset")
        btn_reset.setFixedWidth(200)
        btn_reset.clicked.connect(self._reset_settings)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Layout setzen **nur einmal**
        self.setLayout(layout)

    def save_settings(self, notification=True):
        """
        Saves the current application settings.

        Parameters:
            notification (bool, optional): If True (default), display a confirmation
                or success message after saving. If False, save silently.

        Calls:
            Internally calls the _save_settings() method with the specified notification flag.
        """
        self._save_settings(notification=notification)

    def _browse_speicherort(self):
        """Open a directory dialog to select a storage path."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Speicherort auswählen", self.edit_speicherort.text()
        )
        if dir_path:
            self.edit_speicherort.setText(dir_path)

    def _load_arbeiten(self):
        """Load job entries from the config into the QListWidget."""
        self.list_arbeiten.clear()
        for arbeit in self.config.get("Arbeiten", []):
            self.list_arbeiten.addItem(QListWidgetItem(arbeit))

    def _add_arbeit(self):
        """Add a new job to the list, avoiding duplicates."""
        neue_arbeit = self.edit_neue_arbeit.text().strip()
        if neue_arbeit:
            vorhandene = [
                self.list_arbeiten.item(i).text()
                for i in range(self.list_arbeiten.count())
            ]
            if neue_arbeit not in vorhandene:
                self.list_arbeiten.addItem(neue_arbeit)
                self.edit_neue_arbeit.clear()
            else:
                QMessageBox.information(
                    self, "Info", "Diese Arbeit ist bereits vorhanden."
                )
        else:
            QMessageBox.warning(
                self, "Warnung", "Bitte gib einen Namen für die neue Arbeit ein."
            )

    def _save_settings(self, notification=True):
        """
        Updates and saves the current configuration settings.

        Parameters:
            notification (bool, optional): If True, shows a "Settings saved" message.
                If False, shows a "Settings reset to default" message.
        """
        self.config.update("Speicherort", self.edit_speicherort.text())

        arbeiten = [
            self.list_arbeiten.item(i).text()
            for i in range(self.list_arbeiten.count())
        ]
        self.config.update("Arbeiten", arbeiten)
        self.config.update("Ausgabedokument", self.combo_ausgabe.currentText())
        self.config.update("PDF automatisch öffnen",
                           self.btn_pdf_auto.isChecked())
        self.config.update("Einheit", self.combo_einheit.currentText())

        selected_text = self.dateiname_combo.currentText()
        self.config.update("Name", "Name" in selected_text)
        self.config.update("Datum", "Datum" in selected_text)
        self.config.update("Uhrzeit", "Uhrzeit" in selected_text)
        if not notification:
            QMessageBox.information(self, "Zurückgesetzt",
                                    "Einstellungen wurden auf Standardwerte zurückgesetzt.")
        else:
            QMessageBox.information(self, "Gespeichert",
                                    "Einstellungen wurden gespeichert.")

    def _set_dateiname_combo_from_config(self, config: dict):
        """Sets the filename components combo box based on the given config dictionary."""
        name = config.get("Name", False)
        datum = config.get("Datum", False)
        uhrzeit = config.get("Uhrzeit", False)

        selected = []
        if name:
            selected.append("Name")
        if datum:
            selected.append("Datum")
        if uhrzeit:
            selected.append("Uhrzeit")

        current_text = " + ".join(selected) if selected else "Keine"
        self.dateiname_combo.setCurrentText(current_text)

    def _reset_settings(self):
        """Reset config to defaults and save without notification."""
        self.config.reset_to_defaults()
        defaults = self.config.get_default_config()
        self.edit_speicherort.setText(defaults["Speicherort"])
        self.list_arbeiten.clear()
        for arbeit in defaults["Arbeiten"]:
            self.list_arbeiten.addItem(arbeit)
        self.combo_ausgabe.setCurrentText(defaults["Ausgabedokument"])
        self.combo_einheit.setCurrentText(defaults["Einheit"])
        self._set_dateiname_combo_from_config(defaults)
        self._save_settings(notification=False)
