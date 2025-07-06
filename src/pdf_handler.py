"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import os
import sys
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Image,
    Spacer, Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, landscape

from utils import resource_path
from file_handler import IFileHandler


class PdfHandler(IFileHandler):
    """
    Generates a PDF document from a pandas DataFrame using a given configuration.
    Can include customer data in the header.

    Args:
        config (dict): Must include "pdf_output_path" (folder to save PDFs).
    """

    def __init__(self, config: dict):
        self.config = config
        self.output_path = config.get("Speicherort", ".")
        self.base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), ".."))
        self.logo_path = resource_path(os.path.join(
            "resources", "FarbenWolfLogoTransparent.png"), self.base_dir)
        self.customer_data = {}

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def set_customer_data(self, data: dict):
        """
        Sets customer information for the PDF header.

        Args:
            data (dict): Dictionary containing customer fields like name, address etc.
                         Example: {"Name": "Max Mustermann", "Adresse": "Musterstraße 1", ...}
        """
        translated = {
            "Anrede": data.get("salutation", ""),
            "Nachname": data.get("last_name", ""),
            "Vorname": data.get("first_name", ""),
            "Straße": data.get("street", ""),
            "Hausnummer": data.get("number", ""),
            "PLZ": data.get("postal_code", ""),
            "Ort": data.get("city", "")
        }
        self.customer_data = translated

    def create_file(self, df: pd.DataFrame, filename: str = "bericht.pdf"):
        """
        Creates a PDF from the DataFrame, including logo and customer data.

        Args:
            df (pd.DataFrame): The data to include.
            filename (str): Output filename.
        """
        file_path = os.path.join(self.output_path, filename)
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))

        styles = getSampleStyleSheet()
        elements = []

        # Logo (kleiner und oben rechts)
        logo_width = 150
        logo_height = 50
        logo = None
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=logo_width, height=logo_height)

        # Kundendaten als Paragraph links
        customer_paragraph = None
        if self.customer_data:
            customer_lines = []
            for key, value in self.customer_data.items():
                customer_lines.append(f"<b>{key}:</b> {value}")
            customer_paragraph = Paragraph(
                "<br/>".join(customer_lines), styles["Normal"])

        # Kopfbereich als Tabelle: links Kundendaten, rechts Logo
        if customer_paragraph and logo:
            header_table = Table(
                [[customer_paragraph, logo]],
                colWidths=[doc.width - logo_width - 10, logo_width + 10]
            )
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(header_table)
        elif customer_paragraph:
            elements.append(customer_paragraph)
        elif logo:
            elements.append(logo)

        elements.append(Spacer(1, 15))

        # Tabelle mit Daten
        df = self. append_units(df)
        table_data = [list(df.columns)] + df.astype(str).values.tolist()
        table = Table(table_data, repeatRows=1)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#cccccc")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)
        doc.build(elements)

    def append_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Appends units to column headers for specific columns:
        - 'Länge', 'Breite', 'Höhe1', 'Höhe2' → adds unit (e.g., "Länge [m]")
        - 'Ergebnis' → adds squared unit (e.g., "Ergebnis [m²]")

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: A copy of the input DataFrame with updated column headers.
        """
        df = df.copy()
        einheit = self.config.get("Einheit", "")

        new_columns = []
        for col in df.columns:
            if col in ["Länge", "Breite", "Höhe1", "Höhe2"]:
                new_columns.append(f"{col} [{einheit}]")
            elif col == "Ergebnis":
                new_columns.append(f"{col} [{einheit}²]")
            else:
                # Flächenart oder andere Spalten unverändert
                new_columns.append(col)

        df.columns = new_columns
        return df

    def build_filename(self, customer_data: dict, base_name: str = "bericht") -> str:
        """
        Builds the filename based on configuration flags and customer data.

        Args:
            customer_data (dict): Customer data, e.g., 'last_name', 'first_name'
            base_name (str): Fallback name if no specific name is requested

        Returns:
            str: Constructed filename with .xlsx extension
        """
        parts = []

        # Name hinzufügen, wenn gewünscht
        if self.config.get("Name", False):
            last_name = customer_data.get("last_name", "")
            first_name = customer_data.get("first_name", "")
            name_part = f"{last_name}_{first_name}".strip("_")
            if name_part:
                parts.append(name_part)

        # Datum hinzufügen, wenn gewünscht
        if self.config.get("Datum", False):
            date_str = datetime.now().strftime("%Y-%m-%d")
            parts.append(date_str)

        # Uhrzeit hinzufügen, wenn gewünscht
        if self.config.get("Uhrzeit", False):
            time_str = datetime.now().strftime("%H-%M-%S")
            parts.append(time_str)

        if not parts:
            parts.append(base_name)

        filename = "_".join(parts) + ".pdf"
        return filename
