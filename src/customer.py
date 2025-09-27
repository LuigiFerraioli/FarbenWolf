"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QSizePolicy, QPushButton
)
from PyQt6.QtGui import QIcon

import math


class CustomerBox(QGroupBox):
    """
    A custom widget that encapsulates customer data input fields including:
    salutation, name, and two address sections (customer address and object address).
    """

    def __init__(self, parent=None):
        super().__init__("Kundendaten", parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self._init_ui()

    def set_customer_data(self, data: dict):
        """
        Sets the UI or internal customer data fields from a dictionary with German keys.
        Handles NaN values by setting empty strings.
        """
        def safe_get(key):
            value = data.get(key, "")
            if isinstance(value, float) and math.isnan(value):
                return ""
            return value

        self.combo_salutation.setCurrentText(safe_get("Anrede"))
        self.edit_last_name.setText(safe_get("Nachname"))
        self.edit_first_name.setText(safe_get("Vorname"))

        # Customer Address
        self.customer_street.setText(safe_get("Kunden-Straße"))
        self.customer_number.setText(safe_get("Kunden-Nr."))
        self.customer_postal.setText(safe_get("Kunden-Plz"))
        self.customer_city.setText(safe_get("Kunden-Ort"))

        # Object Address
        self.object_street.setText(safe_get("Objekt-straße"))
        self.object_number.setText(safe_get("Objekt-Nr."))
        self.object_postal.setText(safe_get("Objekt-Plz"))
        self.object_city.setText(safe_get("Objekt-Ort"))

    def get_customer_data(self) -> dict:
        """Returns the current customer input data as a dictionary."""
        return {
            "salutation": self.combo_salutation.currentText(),
            "last_name": self.edit_last_name.text(),
            "first_name": self.edit_first_name.text(),
            "customer_street": self.customer_street.text(),
            "customer_number": self.customer_number.text(),
            "customer_postal": self.customer_postal.text(),
            "customer_city": self.customer_city.text(),
            "object_street": self.object_street.text(),
            "object_number": self.object_number.text(),
            "object_postal": self.object_postal.text(),
            "object_city": self.object_city.text()
        }

    def _init_ui(self):
        """Initialize the UI layout and widgets."""
        main_layout = QVBoxLayout()

        # Top row: Salutation + Name
        top_layout = QHBoxLayout()
        top_layout.addLayout(self._create_salutation_section())
        top_layout.addLayout(self._create_name_section())

        # Button
        button_layout = QVBoxLayout()
        spacer_label = QLabel(" ")
        button_layout.addWidget(spacer_label)

        btn_copy = QPushButton()
        btn_copy.setIcon(QIcon.fromTheme("edit-copy"))
        btn_copy.setToolTip("Kundenadresse kopieren")
        btn_copy.setFixedSize(40, 30)
        btn_copy.clicked.connect(self._copy_customer_adress)
        button_layout.addWidget(btn_copy)
        button_layout.addStretch()

        top_layout.addLayout(button_layout)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)
        main_layout.addSpacing(20)

        # Customer Address Section
        main_layout.addLayout(self._create_address_section(
            prefix="customer_", main_label="Kundenadresse"))
        main_layout.addSpacing(10)
        main_layout.addLayout(self._create_address_section(
            prefix="object_", main_label="Objektadresse"))

        self.setLayout(main_layout)

    def _create_salutation_section(self) -> QVBoxLayout:
        """Create the salutation (title) input layout."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Anrede*"))

        self.combo_salutation = QComboBox()
        self.combo_salutation.addItems(["Herr", "Frau", "Familie"])
        self.combo_salutation.setMinimumWidth(150)
        self.combo_salutation.setMaximumWidth(200)
        self.combo_salutation.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.combo_salutation)
        return layout

    def _create_name_section(self) -> QHBoxLayout:
        """Create the name input layout with first and last name."""
        layout = QHBoxLayout()

        # Last name
        last_name_layout = QVBoxLayout()
        last_name_layout.addWidget(QLabel("Nachname*"))
        self.edit_last_name = QLineEdit()
        self._set_fixed_line_edit(
            self.edit_last_name, min_width=300, max_width=500)
        last_name_layout.addWidget(self.edit_last_name)
        layout.addLayout(last_name_layout)
        layout.addSpacing(10)

        # First name
        first_name_layout = QVBoxLayout()
        first_name_layout.addWidget(QLabel("Vorname"))
        self.edit_first_name = QLineEdit()
        self._set_fixed_line_edit(
            self.edit_first_name, min_width=300, max_width=500)
        first_name_layout.addWidget(self.edit_first_name)
        layout.addLayout(first_name_layout)

        return layout

    def _create_address_section(self, prefix: str = "", main_label: str = "") -> QHBoxLayout:
        """
        Create an address input layout with labels and line edits.

        Args:
            prefix (str): Optional prefix for attribute names (e.g., 'customer_' or 'object_')
        """
        layout = QHBoxLayout()

        # Main label
        if main_label:
            lbl_main = QLabel(main_label)
            lbl_main.setFixedWidth(150)
            layout.addWidget(lbl_main)

        # Street
        street_layout = QVBoxLayout()
        street_layout.addWidget(QLabel("Straße"))
        line_edit_street = QLineEdit()
        self._set_fixed_line_edit(
            line_edit_street, min_width=300, max_width=500)
        street_layout.addWidget(line_edit_street)
        setattr(self, f"{prefix}street", line_edit_street)
        layout.addLayout(street_layout)
        layout.addSpacing(10)

        # House number
        number_layout = QVBoxLayout()
        number_layout.addWidget(QLabel("Nr."))
        line_edit_number = QLineEdit()
        self._set_fixed_line_edit(line_edit_number, max_width=70)
        number_layout.addWidget(line_edit_number)
        setattr(self, f"{prefix}number", line_edit_number)
        layout.addLayout(number_layout)
        layout.addSpacing(10)

        # Postal code
        postal_layout = QVBoxLayout()
        postal_layout.addWidget(QLabel("Postleitzahl"))
        line_edit_postal = QLineEdit()
        self._set_fixed_line_edit(line_edit_postal, max_width=100)
        postal_layout.addWidget(line_edit_postal)
        setattr(self, f"{prefix}postal", line_edit_postal)
        layout.addLayout(postal_layout)
        layout.addSpacing(10)

        # City
        city_layout = QVBoxLayout()
        city_layout.addWidget(QLabel("Stadt"))
        line_edit_city = QLineEdit()
        self._set_fixed_line_edit(line_edit_city, min_width=300)
        city_layout.addWidget(line_edit_city)
        setattr(self, f"{prefix}city", line_edit_city)
        layout.addLayout(city_layout)

        return layout

    def _set_fixed_line_edit(self, line_edit: QLineEdit, min_width: int = None, max_width: int = None):
        """Helper to set fixed sizing and policy for QLineEdit widgets."""
        if min_width:
            line_edit.setMinimumWidth(min_width)
        if max_width:
            line_edit.setMaximumWidth(max_width)
        if min_width or max_width:
            line_edit.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            line_edit.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _copy_customer_adress(self):
        """Copy all customer address fields into the object address fields."""
        self.object_street.setText(self.customer_street.text())
        self.object_number.setText(self.customer_number.text())
        self.object_postal.setText(self.customer_postal.text())
        self.object_city.setText(self.customer_city.text())
