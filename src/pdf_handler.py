"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import os
import sys
import subprocess
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
            "resources", "LogoTransparent.png"), self.base_dir)
        self.customer_data = {}

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def set_customer_data(self, data: dict):
        self.customer_data = data

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

        # Logo
        logo_width = 150
        logo_height = 50
        logo = None
        if os.path.exists(self.logo_path):
            logo = Image(self.logo_path, width=logo_width, height=logo_height)

        # Kundendaten in drei Spalten
        if self.customer_data:
            customer_lines = list(self.customer_data.items())

            # Aufteilung: 3 + 4 + 4 Zeilen
            col1 = customer_lines[:3]
            col2 = customer_lines[3:7]
            col3 = customer_lines[7:11]

            def make_paragraphs(lines):
                return [Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]) for k, v in lines]

            col1_par = make_paragraphs(col1)
            col2_par = make_paragraphs(col2)
            col3_par = make_paragraphs(col3)

            # Spalten auf gleiche Länge bringen
            max_len = max(len(col1_par), len(col2_par), len(col3_par))
            for col in (col1_par, col2_par, col3_par):
                while len(col) < max_len:
                    col.append(Paragraph("", styles["Normal"]))

            # Tabelle mit drei Spalten
            customer_table_data = list(zip(col1_par, col2_par, col3_par))
            customer_table = Table(customer_table_data)
            customer_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

            # Äußere Tabelle: links Kundendaten, rechts Logo
            outer_table_data = [[customer_table, logo if logo else ""]]
            outer_table = Table(outer_table_data, colWidths=[
                                doc.width - logo_width - 10, logo_width + 10])
            outer_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(outer_table)

        elements.append(Spacer(1, 15))

        # Tabelle mit Daten
        df = self.append_units(df)
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

        if self.config.get("PDF automatisch öffnen", True):
            self.open_pdf(file_path)

    def open_pdf(self, file_path):
        """
        Opens a PDF file using the default system application.

        Supports Windows, macOS, and Linux. If the file cannot be opened,
        an error message is printed to the console.

        Args:
            file_path (str): The full path to the PDF file to open.
        """
        try:
            if sys.platform.startswith("win"):
                os.startfile(file_path)  # Windows
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", file_path])  # macOS
            else:
                subprocess.run(["xdg-open", file_path])  # Linux
        except Exception as e:
            print(f"Fehler beim Öffnen der PDF: {e}")

    def append_units(self, df: pd.DataFrame) -> pd.DataFrame:
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
        parts = []

        # Add name if requested
        if self.config.get("Name", False):
            last_name = customer_data.get("Nachname", "")
            first_name = customer_data.get("Vorname", "")
            name_part = f"{last_name}_{first_name}".strip("_")
            if name_part:
                parts.append(name_part)

        # Add date if requested
        if self.config.get("Datum", False):
            date_str = datetime.now().strftime("%Y-%m-%d")
            parts.append(date_str)

        # Add time if requested
        if self.config.get("Uhrzeit", False):
            time_str = datetime.now().strftime("%H-%M-%S")
            parts.append(time_str)

        if not parts:
            parts.append(base_name)

        filename = "_".join(parts) + ".pdf"
        return filename

    def set_save_path(self, path: str) -> None:
        if not os.path.isdir(path):
            raise ValueError(f"Invalid directory: {path}")
        self.save_path = path
