"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout,
    QTextEdit, QComboBox, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QSizePolicy, QFileDialog)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import pandas as pd
import re

from customer import CustomerBox
from calculator import Calculator
from pdf_handler import PdfHandler
from excel_handler import ExcelHandler
from plotter import FlaechenPlotter


class SurveyTab(QWidget):
    """
    A tab page for creating a survey/document based on customer data.
    """

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.table_columns = ["Pos.", "Stk.", "Länge", "Breite", "Höhe1", "Höhe2",
                              "Flächenart", "Ergebnis", "Arbeit", "Bemerkung"]

        self.df = pd.DataFrame(
            [[""] * len(self.table_columns)], columns=self.table_columns)
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.table_columns))
        self.table_widget.setHorizontalHeaderLabels(self.table_columns)

        self._init_ui()
        self.update_field_availability_for_flaeche()
        self.combo_pos.currentIndexChanged.connect(self.load_entry_from_pos)
        self.combo_flaeche.currentTextChanged.connect(
            self.update_field_availability_for_flaeche)
        self.plotter = FlaechenPlotter()
        self.is_file_up_to_date = True

    def close_plotter(self):
        """ Closes the plotter window if it is currently open."""
        if hasattr(self, "plotter"):
            self.plotter.close_figure()

    def generate_survey(self, path_to_save=None) -> bool:
        """
        Generates a survey or document based on the current customer data and configuration.

        Args:
            path_to_save (str, optional): Folder path where the file should be saved. Defaults to None.

        Returns:
            bool: True if the survey was successfully generated, False otherwise.
        """
        self.update_ui_from_config()
        customer_data = self.customerbox.get_customer_data()

        if not self._validate_customer_data(customer_data):
            return False

        customer_data = self.customerbox.get_translated_customer_data()
        result_df = self._prepare_dataframe(self.df)

        document_type = self.config.get("Ausgabedokument")
        handlers = self._get_handlers(
            document_type, path_to_save, customer_data)

        for handler in handlers:
            handler.create_file(
                result_df, handler.build_filename(customer_data))

        QMessageBox.information(
            self, "Export", f"Das Ergebnis wurde als {document_type} exportiert.")

        self.set_save_status(True)
        return True

    def save(self) -> None:
        """
        Saves the file using the current configuration and customer data.

        The file is generated and saved to the default or previously configured save path.
        If no path is set, the method may use a default location or handle path selection internally.

        Raises:
            RuntimeError: If the file cannot be saved due to missing configuration or invalid path.
        """
        self.generate_survey(path_to_save=None)

    def save_under(self) -> None:
        """
        Opens a folder selection dialog and saves the file to the selected folder.

        The user can choose a folder, which will be stored as the save path.
        After selecting the folder, the file is generated and saved there.

        Raises:
            RuntimeError: If folder selection is cancelled.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Save File",
            self.config.get("Speicherort", ".")
        )

        if not folder_path:
            return

        # Generate and save the file
        self.generate_survey(path_to_save=folder_path)

    def import_survey(self):
        """
        Opens a file dialog to select an Excel file and loads it into a DataFrame.
        Also loads customer data if available.
        """
        if not self.check_save_before_action():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            self.config.get("Speicherort", "."),
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if file_path:
            try:
                excel_handler = ExcelHandler(self.config)
                customer_data, data_df = excel_handler.load_file(
                    file_path, self.table_columns)

                if customer_data is not None and data_df is not None:
                    self.customerbox.set_customer_data(customer_data)
                    self.df = data_df

                    empty_row = pd.Series(
                        [""] * len(self.table_columns), index=self.table_columns)
                    self.df = pd.concat(
                        [self.df, empty_row.to_frame().T], ignore_index=True)
                    self.update_table_area()
                    self.update_pos_items()
                    self.set_save_status(True)
                else:
                    QMessageBox.warning(
                        self, "Error",
                        "Die ausgewählte Datei konnte nicht geladen werden oder ist beschädigt."
                    )

            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Fehler beim Laden der Exceldatei:\n{e}")
        else:
            QMessageBox.information(self, "Import", "Keine Datei ausgewählt.")

    def new_survey(self):
        """
        Starts a new survey after optionally saving the current one.
        """
        if not self.check_save_before_action():
            return

        self.delete_actual_survey()
        self.customerbox.clear_inputs()
        self.set_save_status(True)

    def check_save_before_action(self) -> bool:
        """
        Checks if the current file is up to date.
        If not, asks the user whether to save it before proceeding.

        Returns:
            bool: True if it is safe to proceed (file saved or user chose not to save),
                False if the action should be cancelled.
        """
        if self.is_file_up_to_date:
            return True

        reply = QMessageBox.question(
            self,
            "Speichern prüfen",
            "Möchten Sie das aktuelle Aufmaß speichern, bevor Sie fortfahren?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.generate_survey():
                return True
        elif reply == QMessageBox.StandardButton.No:
            return True
        return False

    def handle_add_entry(self):
        """
        Handles the action of adding a new entry to the data or list.

        Typically triggered by a user event (e.g., button click),
        this method processes the input and updates the relevant data structure.
        """
        try:
            length = self._parse_number_or_raise(
                self.input_length.text(), "Länge")
            width = self._parse_number_or_raise(
                self.input_width.text(), "Breite")
            height1 = self._parse_number_or_raise(
                self.input_height1.text(), "Höhe1")
            height2 = self._parse_number_or_raise(
                self.input_height2.text(), "Höhe2")
            stk = self._parse_number_or_raise(
                self.input_stk.text(), "Stk.")
        except ValueError as e:
            QMessageBox.warning(self, "Ungültige Eingabe", str(e))
            return

        # Werte sammeln
        pos = self.combo_pos.currentText()
        flaeche = self.combo_flaeche.currentText()
        arbeit = self.combo_arbeiten.currentText()
        note = self.input_note.text()

        result = Calculator(self.config).calculate_single(
            flaechenart=flaeche,
            laenge=length,
            breite=width,
            hoehe1=height1,
            hoehe2=height2,
            stk=stk
        )

        stk = self.input_stk.text().strip()
        if not stk:
            stk = "1"  # Default, if empty

        # Create new row with 'Stk.' at the second position (index 1)
        new_row = pd.Series(
            [pos, stk, length, width, height1, height2,
                flaeche, result, arbeit, note],
            index=self.table_columns)

        existing_index = self._find_existing_pos_index(pos)

        if not existing_index.empty:
            # Replace existing
            self.df.loc[existing_index[0]] = new_row

        else:
            # Insert new row before the last empty one, if it exists and is really empty
            last_row = self.df.iloc[-1]
            if (
                last_row.isnull().all()
                or all(str(v).strip() == "" for v in last_row)
            ):
                self.df.iloc[-1] = new_row
            else:
                self.df = pd.concat(
                    [self.df, new_row.to_frame().T], ignore_index=True)

            # Add new empty row
            empty_row = pd.Series(
                [""] * len(self.table_columns), index=self.table_columns)
            self.df = pd.concat(
                [self.df, empty_row.to_frame().T], ignore_index=True)

        self.update_table_area()
        self.clear_inputs()

    def update_table_area(self):
        """
        Updates the table widget to reflect the current DataFrame contents.

        Sets row and column counts, headers, and fills cells with centered data.
        Also updates the position dropdown items.
        """
        self.update_ui_from_config()
        self.table_widget.setRowCount(len(self.df))
        self.table_widget.setColumnCount(len(self.df.columns))
        self.table_widget.setHorizontalHeaderLabels(self.df.columns.tolist())

        for row in range(len(self.df)):
            for col in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iat[row, col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_widget.setItem(row, col, item)
        self.update_pos_items()
        self.set_save_status(False)

    def handle_delete_entry(self):
        """
        Deletes the selected entry from the DataFrame based on the position.

        Renumbers positions, removes empty rows if any, and updates the UI.
        """
        pos_to_delete = self.combo_pos.currentText().strip()
        if not pos_to_delete:
            return
        index = self._find_existing_pos_index(pos_to_delete)

        # Delete the row(s)
        self.df = self.df.drop(index=index).reset_index(drop=True)

        # Temporarily remove empty row if present (e.g., at the end)
        has_empty_row = self.df.iloc[-1].isnull().all() or all(
            str(v).strip() == "" for v in self.df.iloc[-1]
        )
        if has_empty_row:
            self.df = self.df.iloc[:-1]

        # Renumber the "Pos." column (1, 2, 3, ...)
        self.df["Pos."] = [str(i + 1) for i in range(len(self.df))]

        # Append an empty row again
        empty_row = pd.Series(
            [""] * len(self.table_columns), index=self.table_columns)
        self.df = pd.concat(
            [self.df, empty_row.to_frame().T], ignore_index=True)

        self.update_table_area()
        self.update_pos_items()

    def delete_actual_survey(self):
        """
        Clears the entire survey, keeping only the column headers.
        Resets the table and position items.
        """
        self.df = pd.DataFrame(columns=self.table_columns)
        empty_row = pd.Series(
            [""] * len(self.table_columns), index=self.table_columns)
        self.df = pd.concat(
            [self.df, empty_row.to_frame().T], ignore_index=True)

        # UI aktualisieren
        self.update_table_area()
        self.update_pos_items()

    def handle_plotter_entry(self):
        """
        Reads input values, validates them, and updates the plotter parameters.

        Shows a warning message if input validation fails.
        """
        try:
            length = self._parse_number_or_raise(
                self.input_length.text(), "Länge")
            width = self._parse_number_or_raise(
                self.input_width.text(), "Breite")
            height1 = self._parse_number_or_raise(
                self.input_height1.text(), "Höhe1")
            height2 = self._parse_number_or_raise(
                self.input_height2.text(), "Höhe2")
        except ValueError as e:
            QMessageBox.warning(self, "Ungültige Eingabe", str(e))
            return

        flaeche = self.combo_flaeche.currentText()

        # Parameter an bestehende Instanz übergeben
        self.plotter.set_parameters(length, width, height1, height2, flaeche)
        self.plotter.plot()

    def update_ui_from_config(self):
        """
        Updates UI elements (comboboxes, placeholders) based on current configuration.
        """
        self.combo_flaeche.clear()
        self.combo_flaeche.addItems(self.config.get("Flächenarten", []))
        index = self.combo_flaeche.findText("Alle Wände mit Decke")
        if index >= 0:
            self.combo_flaeche.setCurrentIndex(index)

        self.combo_arbeiten.clear()
        self.combo_arbeiten.addItems(self.config.get("Arbeiten", []))

        self._set_placeholder_with_unit(self.input_length)
        self._set_placeholder_with_unit(self.input_width)
        self._set_placeholder_with_unit(self.input_height1)
        self._set_placeholder_with_unit(self.input_height2)

    def update_pos_items(self):
        """
        Updates the position combobox with the current positions from the DataFrame.

        Selects the largest position by default.
        """
        self.combo_pos.clear()
        row_count = len(self.df)  # Oder self.table_widget.rowCount()
        if row_count == 0:
            self.combo_pos.addItem("1")
        else:
            items = [str(i) for i in range(1, row_count + 1)]
            self.combo_pos.addItems(items)
            # Größtes Element auswählen (Index: len(items) - 1)
            self.combo_pos.setCurrentIndex(len(items) - 1)

    def load_entry_from_pos(self):
        """
        Loads data from the DataFrame into input fields based on the selected position.

        Clears inputs if the position does not exist.
        """
        selected_pos = self.combo_pos.currentText()
        if not selected_pos:
            return

        # Prüfen, ob diese Pos. überhaupt existiert
        df_index = self._find_existing_pos_index(selected_pos)
        if df_index.empty:
            self.clear_inputs()
            return

        # Existiert → Daten laden
        row = self.df.loc[df_index[0]]
        self.input_stk.setText(str(row["Stk."]))
        self.input_length.setText(str(row["Länge"]))
        self.input_width.setText(str(row["Breite"]))
        self.input_height1.setText(str(row["Höhe1"]))
        self.input_height2.setText(str(row["Höhe2"]))
        self.input_note.setText(str(row["Bemerkung"]))

        index_flaeche = self.combo_flaeche.findText(str(row["Flächenart"]))
        if index_flaeche >= 0:
            self.combo_flaeche.blockSignals(True)
            self.combo_flaeche.setCurrentIndex(index_flaeche)
            self.combo_flaeche.blockSignals(False)
            self.update_field_availability_for_flaeche()

        index_arbeit = self.combo_arbeiten.findText(str(row["Arbeit"]))
        if index_arbeit >= 0:
            self.combo_arbeiten.setCurrentIndex(index_arbeit)

    def update_field_availability_for_flaeche(self):
        """
        Enables or disables input fields depending on the selected surface type (Flächenart).

        Disables and sets default values for fields that are not relevant for the selected type.
        """
        flaeche = self.combo_flaeche.currentText()

        # Alle Felder aktivieren und leeren
        for field in [self.input_length, self.input_width, self.input_height1, self.input_height2]:
            field.setReadOnly(False)
            field.setDisabled(False)
            if field.text() == "0.0":
                field.setText("")

        def disable(field):
            field.setText("0.0")
            field.setReadOnly(True)
            field.setDisabled(True)

        # Felder abhängig von der Flächenart deaktivieren
        if flaeche in ["Decke/Bodenfläche"]:
            disable(self.input_height1)
            disable(self.input_height2)
        elif flaeche in ["Wand (rechteckig)", "Wand (dreieckig)", "Zwei gegenüberliegende Wände"]:
            disable(self.input_width)
            disable(self.input_height2)
        elif flaeche in ["Zwei nebeneinanderliegende Wände", "Fassade (Flachdach)",
                         "Alle Wände ohne Decke/Sockel", "Alle Wände mit Decke"]:
            disable(self.input_height2)

    def clear_inputs(self):
        """
        Clears all input fields and updates their availability based on the selected surface type.
        """
        self.input_length.clear()
        self.input_width.clear()
        self.input_height1.clear()
        self.input_height2.clear()
        self.input_note.clear()
        self.update_field_availability_for_flaeche()

    def set_save_status(self, saved: bool):
        """
        Updates the save status icon.
        Uses system's disabled/enabled look instead of manual alpha manipulation.

        Args:
            saved (bool): True if the file is up to date, False otherwise.
        """
        self.is_file_up_to_date = saved
        icon = QIcon.fromTheme("document-save")
        pixmap = icon.pixmap(24, 24)
        self.save_status_label.setEnabled(saved)
        self.save_status_label.setPixmap(pixmap)

    def _find_existing_pos_index(self, pos_value: str) -> pd.Index:
        """
        Finds the index of the row where 'Pos.' matches the given value,
        trying both string and integer representations.

        Args:
            pos_value (str): The position to search for.

        Returns:
            pd.Index: Index of matching row(s), or empty Index if none found.
        """
        try:
            pos_int = int(pos_value)
            return self.df[(self.df["Pos."] == pos_value) | (self.df["Pos."] == pos_int)].index
        except ValueError:
            return self.df[self.df["Pos."] == pos_value].index

    def _parse_number_or_raise(self, text: str, feldname: str) -> float:
        """
        Parses a string to float, replacing commas with dots.
        Evaluates simple arithmetic expressions like 5+5, 3.5 + 7, 10.0-0.4.

        Raises:
            ValueError: If the string cannot be converted to a valid float.

        Parameters:
            text (str): The string to parse or evaluate.
            feldname (str): The name of the field for error messages.

        Returns:
            float: The parsed or evaluated number.
        """
        text = text.strip().replace(",", ".")
        # Erlaubte Zeichen: Ziffern, Punkt, +, -, *, /, Klammern und Leerzeichen
        error_text = \
            f"Ungültige Eingabe für '{feldname}'. Bitte gib eine Zahl oder einfachen Ausdruck ein."
        if not re.match(r"^[0-9\.\+\-\*\/\(\) ]+$", text):
            raise ValueError(error_text)
        try:
            result = eval(text)
            return float(result)
        except Exception as exc:
            raise ValueError(error_text) from exc

    def _set_placeholder_with_unit(self, field):
        field.setPlaceholderText(f"in {self.config.get('Einheit')}")

    def _init_ui(self):
        """Initializes the user interface components."""
        layout = QVBoxLayout()

        # CustomerBox
        self.customerbox = CustomerBox()
        layout.addWidget(self.customerbox)
        layout.addSpacing(20)

        self._init_table_widget()
        layout.addWidget(self.table_widget, stretch=1)
        layout.addSpacing(20)

        self._add_table_header_labels(layout)
        self._add_entry_fields(layout)
        self._add_button_row(layout)

        self.setLayout(layout)

    def _init_table_widget(self):
        """Initializes the table widget with column headers and sizes."""
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(self.table_columns))
        self.table_widget.setHorizontalHeaderLabels(self.table_columns)

        header = self.table_widget.horizontalHeader()
        resize_modes = [50, 50, 100, 100, 100, 100, 400,
                        100, 200, None]  # Last column = stretch

        for i, width in enumerate(resize_modes):
            mode = QHeaderView.ResizeMode.Stretch if width is None else QHeaderView.ResizeMode.Fixed
            header.setSectionResizeMode(i, mode)
            if width is not None:
                self.table_widget.setColumnWidth(i, width)

        self.table_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_widget.setRowCount(1)
        for col in range(len(self.table_columns)):
            self.table_widget.setItem(0, col, QTableWidgetItem(""))

    def _add_table_header_labels(self, layout):
        """Adds the header labels above the entry row."""
        header_layout = QHBoxLayout()
        label_specs = [
            ("Pos.", 50), ("Stk.", 50), ("Länge", 100), ("Breite", 100),
            ("Höhe1", 100), ("Höhe2", 100), ("Flächenart", 400),
            ("Arbeit", 300), ("Bemerkung", None)
        ]
        for text, width in label_specs:
            label = QLabel(text)
            if width:
                label.setFixedWidth(width)
            header_layout.addWidget(label)
        header_layout.addSpacing(70)
        layout.addStretch()
        layout.addLayout(header_layout)

    def _add_entry_fields(self, layout):
        """Adds entry row widgets."""
        entry_layout = QHBoxLayout()

        # Position & Stück
        self.combo_pos = QComboBox()
        self.combo_pos.addItem("1")
        self.combo_pos.setFixedWidth(50)
        entry_layout.addWidget(self.combo_pos)

        self.input_stk = QLineEdit("1")
        self.input_stk.setFixedWidth(50)
        entry_layout.addWidget(self.input_stk)

        # Länge, Breite, Höhe1, Höhe2
        for attr_name in ["input_length", "input_width", "input_height1", "input_height2"]:
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"in {self.config.get('Einheit')}")
            line_edit.setFixedWidth(100)
            setattr(self, attr_name, line_edit)
            entry_layout.addWidget(line_edit)

        # Flächenart Dropdown
        self.combo_flaeche = QComboBox()
        self.combo_flaeche.addItems(self.config.get("Flächenarten", []))
        self.combo_flaeche.setFixedWidth(400)
        index = self.combo_flaeche.findText("Alle Wände mit Decke")
        if index >= 0:
            self.combo_flaeche.setCurrentIndex(index)
        entry_layout.addWidget(self.combo_flaeche)

        # Arbeiten Dropdown
        self.combo_arbeiten = QComboBox()
        self.combo_arbeiten.addItems(self.config.get("Arbeiten", []))
        self.combo_arbeiten.setFixedWidth(150)
        entry_layout.addWidget(self.combo_arbeiten)

        # Bemerkung
        self.input_note = QLineEdit()
        self.input_note.setPlaceholderText("Bemerkung")
        entry_layout.addWidget(self.input_note)

        # Action Buttons
        self._add_icon_button(entry_layout, "list-add",
                              "Add entry", self.handle_add_entry)
        self._add_icon_button(entry_layout, "edit-delete",
                              "Delete entry", self.handle_delete_entry)
        self._add_icon_button(entry_layout, "system-search",
                              "Plotter entry", self.handle_plotter_entry)

        layout.addLayout(entry_layout)
        layout.addSpacing(20)

    def _add_icon_button(self, layout, icon_name, tooltip, callback):
        """Adds a small icon button to a layout."""
        button = QPushButton()
        button.setIcon(QIcon.fromTheme(icon_name))
        button.setToolTip(tooltip)
        button.setFixedSize(64, 32)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def _add_button_row(self, layout):
        """Adds the bottom button row (Import, Generate Survey) with a save status icon."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # --- Save Status Icon ---
        self.save_status_label = QLabel()
        save_icon = QIcon.fromTheme("document-save")
        self.save_status_label.setPixmap(
            save_icon.pixmap(24, 24))
        button_layout.addWidget(self.save_status_label)
        button_layout.addSpacing(10)

        # --- Import Button ---
        self.btn_import = QPushButton(" Import")
        self.btn_import.setIcon(QIcon.fromTheme("folder-new"))
        self.btn_import.setFixedWidth(250)
        self.btn_import.clicked.connect(self.import_survey)

        # --- Generate Survey Button ---
        self.btn_generate_survey = QPushButton(" Speichern")
        self.btn_generate_survey.setIcon(QIcon.fromTheme("document-save"))
        self.btn_generate_survey.setFixedWidth(250)
        self.btn_generate_survey.clicked.connect(self.save)

        # --- Save Under Button ---
        self.btn_generate_survey_save_under = QPushButton(" Speichern unter")
        self.btn_generate_survey_save_under.setIcon(
            QIcon.fromTheme("document-save-as"))
        self.btn_generate_survey_save_under.setFixedWidth(250)
        self.btn_generate_survey_save_under.clicked.connect(self.save_under)

        # --- New Survey Button ---
        self.btn_new = QPushButton(" Neues Aufmaß")
        self.btn_new.setIcon(QIcon.fromTheme("document-new"))
        self.btn_new.setFixedWidth(250)
        self.btn_new.clicked.connect(self.new_survey)

        # --- Add buttons to layout ---
        button_layout.addWidget(self.btn_import)
        button_layout.addSpacing(1)
        button_layout.addWidget(self.btn_generate_survey)
        button_layout.addSpacing(1)
        button_layout.addWidget(self.btn_generate_survey_save_under)
        button_layout.addStretch(1)
        button_layout.addWidget(self.btn_new)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _validate_customer_data(self, customer_data: dict) -> bool:
        if len(customer_data.get("last_name", "").strip()) < 2:
            QMessageBox.information(
                self, "Kundendaten",
                "Der Nachname des Kunden muss angegeben werden (mindestens 3 Zeichen)."
            )
            return False

        first_row = self.df.iloc[0]
        wertefelder = ["Länge", "Breite", "Höhe1", "Höhe2"]
        if not any(pd.notna(first_row[f])
                   and str(first_row[f]).strip() not in ("", "0", "0.0") for f in wertefelder):
            QMessageBox.warning(
                self, "Ungültiger Eintrag",
                "Mindestens eines der Felder Länge, Breite, Höhe1 oder Höhe2"
                "muss einen Wert enthalten."
            )
            return False
        return True

    def _prepare_dataframe(self, df):
        last_row = df.iloc[-1]
        if any(pd.isna(last_row[f]) or last_row[f] == ""
               for f in ["Länge", "Breite", "Höhe1", "Höhe2"]):
            return df[:-1].copy()
        return df

    def _get_handlers(self, document_type: str, path_to_save: str, customer_data: dict):
        handlers = []

        if document_type in ("pdf", "pdf & excel"):
            pdf_handler = PdfHandler(self.config)
            if path_to_save:
                pdf_handler.set_save_path(path_to_save)
            pdf_handler.set_customer_data(customer_data)
            handlers.append(pdf_handler)

        if document_type in ("excel", "pdf & excel"):
            excel_handler = ExcelHandler(self.config)
            if path_to_save:
                excel_handler.set_save_path(path_to_save)
            excel_handler.set_customer_data(customer_data)
            handlers.append(excel_handler)

        return handlers
