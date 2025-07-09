"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QSizePolicy
)

import math


class CustomerBox(QGroupBox):
    """
    A custom widget that encapsulates customer data input fields including:
    salutation, name, and address fields (street, number, postal code, city).
    """

    def __init__(self, parent=None):
        super().__init__("Kundendata", parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self._init_ui()

    def set_customer_data(self, data: dict):
        """
        Sets the UI or internal customer data fields from a dictionary with German keys.
        Handles NaN values by setting empty strings.

        Args:
            data (dict): Customer data dict with keys like 'Anrede', 'Nachname', etc.
        """
        def safe_get(key):
            value = data.get(key, "")
            # If value is NaN (float), convert to empty string
            if isinstance(value, float) and math.isnan(value):
                return ""
            return value

        self.combo_salutation.setCurrentText(safe_get("Anrede"))
        self.edit_last_name.setText(safe_get("Nachname"))
        self.edit_first_name.setText(safe_get("Vorname"))
        self.edit_street.setText(safe_get("Straße"))
        self.edit_number.setText(safe_get("Hausnummer"))
        self.edit_postal.setText(safe_get("PLZ"))
        self.edit_city.setText(safe_get("Ort"))

    def get_customer_data(self) -> dict:
        """
        Returns the current customer input data as a dictionary.
        """
        return {
            "salutation": self.combo_salutation.currentText(),
            "last_name": self.edit_last_name.text(),
            "first_name": self.edit_first_name.text(),
            "street": self.edit_street.text(),
            "number": self.edit_number.text(),
            "postal_code": self.edit_postal.text(),
            "city": self.edit_city.text()
        }

    def _init_ui(self):
        """Initialize the UI layout and widgets."""
        main_layout = QVBoxLayout()
        horizontal_layout = QHBoxLayout()

        # Add field sections
        horizontal_layout.addLayout(self._create_salutation_section())
        horizontal_layout.addSpacing(20)
        horizontal_layout.addLayout(self._create_name_section())
        horizontal_layout.addSpacing(40)
        horizontal_layout.addLayout(self._create_address_section())
        horizontal_layout.addStretch()
        main_layout.addLayout(horizontal_layout)
        self.setLayout(main_layout)

    def _create_salutation_section(self) -> QVBoxLayout:
        """Create the salutation (title) input layout."""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Anrede*"))

        self.combo_salutation = QComboBox()
        self.combo_salutation.addItems(["Herr", "Frau", "Familie"])
        self.combo_salutation.setMaximumWidth(100)
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
        layout.addSpacing(20)

        # First name
        first_name_layout = QVBoxLayout()
        first_name_layout.addWidget(QLabel("Vorname"))
        self.edit_first_name = QLineEdit()
        self._set_fixed_line_edit(
            self.edit_first_name, min_width=300, max_width=500)
        first_name_layout.addWidget(self.edit_first_name)
        layout.addLayout(first_name_layout)

        return layout

    def _create_address_section(self) -> QHBoxLayout:
        """Create the address input layout."""
        layout = QHBoxLayout()

        # Street
        street_layout = QVBoxLayout()
        street_layout.addWidget(QLabel("Straße"))
        self.edit_street = QLineEdit()
        self._set_fixed_line_edit(
            self.edit_street, min_width=300, max_width=500)
        street_layout.addWidget(self.edit_street)
        layout.addLayout(street_layout)
        layout.addSpacing(10)

        # House number
        number_layout = QVBoxLayout()
        number_layout.addWidget(QLabel("Nr."))
        self.edit_number = QLineEdit()
        self._set_fixed_line_edit(self.edit_number, max_width=70)
        number_layout.addWidget(self.edit_number)
        layout.addLayout(number_layout)
        layout.addSpacing(10)

        # Postal code
        postal_layout = QVBoxLayout()
        postal_layout.addWidget(QLabel("Postleitzahl"))
        self.edit_postal = QLineEdit()
        self._set_fixed_line_edit(self.edit_postal, max_width=100)
        postal_layout.addWidget(self.edit_postal)
        layout.addLayout(postal_layout)
        layout.addSpacing(10)

        # City
        city_layout = QVBoxLayout()
        city_layout.addWidget(QLabel("Stadt"))
        self.edit_city = QLineEdit()
        self._set_fixed_line_edit(self.edit_city, min_width=300, max_width=500)
        city_layout.addWidget(self.edit_city)
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
