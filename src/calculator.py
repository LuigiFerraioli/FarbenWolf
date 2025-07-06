"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import pandas as pd
import math


class Calculator:
    """
    Calculator for computing area values based on given configurations
    and dimensional inputs.

    Args:
        config (dict, optional): Optional configuration dictionary, e.g., for supported area types.
    """

    def __init__(self, config: dict = None):
        """
        Initializes the Calculator. No DataFrame is required upon initialization.

        Args:
            config (dict, optional): Optional configuration dictionary.
        """
        self.config = config or {}
        self.result_column = "Ergebnis"  # Keep column name in German

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates the area values for each row in the given DataFrame based on
        'Flächenart', 'Länge', 'Breite', 'Höhe1' and 'Höhe2'.

        Args:
            df (pd.DataFrame): DataFrame with columns:
                               'Flächenart', 'Länge', 'Breite', 'Höhe1','Höhe2'
2

        Returns:
            pd.DataFrame: A copy of the input DataFrame with an additional 'Ergebnis' column.
        """
        df = df.copy()
        df[self.result_column] = None

        for idx, row in df.iterrows():
            try:
                flaeche = row["Flächenart"]
                laenge = self._parse_float(row["Länge"])
                breite = self._parse_float(row["Breite"])
                hoehe1 = self._parse_float(row["Höhe1"])
                hoehe2 = self._parse_float(row["Höhe2"])

                result = self._berechne_flaeche(
                    flaeche, laenge, breite, hoehe1, hoehe2)
                df.at[idx, self.result_column] = result
            except Exception as e:
                df.at[idx, self.result_column] = f"Error: {e}"

        return df

    def calculate_single(self, flaechenart: str, laenge, breite, hoehe1, hoehe2, stk=1) -> float:
        """
        Quick area calculation for a single set of values.

        Args:
            flaechenart (str): Flächenart (e.g. "Bodenfläche", "Wand (rechteckig)", etc.)
            laenge, breite, hoehe: Input values (float or strings with comma/dot).

        Returns:
            float: Computed area

        Raises:
            ValueError: On invalid input or unknown area type.
        """
        l = self._parse_float(laenge)
        b = self._parse_float(breite)
        h1 = self._parse_float(hoehe1)
        h2 = self._parse_float(hoehe2)
        stk = self._parse_float(stk)
        return round(self._berechne_flaeche(flaechenart, l, b, h1, h2) * stk, 2)

    def _berechne_flaeche(self, art: str, l: float, b: float, h1: float, h2: float) -> float:
        """
        Calculates area based on 'Flächenart' and the given dimensions.

        Args:
            art (str): Flächenart (area type in German).
            l (float): Länge
            b (float): Breite
            h1 (float): Höhe1
            h2 (float): Höhe2
            stk (int): Stückzahl

        Returns:
            float: Calculated area

        Raises:
            ValueError: If the area type is unknown.
        """
        if h2 != 0 and h1 > h2:
            h1, h2 = h2, h1
        if art == "Decke/Bodenfläche":
            return l * b
        if art == "Wand (rechteckig)":
            return l * h1
        if art == "Wand (dreieckig)":
            return 0.5 * l * h1
        if art == "Zwei gegenüberliegende Wände":
            return 2 * l * h1
        if art == "Zwei nebeneinanderliegende Wände":
            return (l + b) * h1
        if art == "Alle Wände ohne Decke/Sockel":
            return 2 * h1 * (l + b)
        if art == "Alle Wände mit Decke":
            return 2 * h1 * (l + b) + (l * b)
        if art == "Alle Wände mit einer schrägen Wand (ohne Decke)":
            schräge_wand = 0.5 * l * abs(h2 - h1) + l * h1
            return 2 * schräge_wand + b * (h2 + h1)
        if art == "Alle Wände mit einer schrägen Wand und Decke":
            schräge_wand = 0.5 * l * abs(h2 - h1) + l * h1
            return 2 * schräge_wand + b * (h2 + h1 + math.sqrt(l**2 + abs(h2 - h1)**2))
        if art == "Fassade (Flachdach)":
            return 2 * h1 * (l + b)
        if art == "Fassade (Satteldach)":
            return 2 * h1 * (l + b) + l * abs(h2 - h1)
        if art == "Fassade (Doppelhaushälfte)":
            schräge_wand = 0.5 * l * abs(h2 - h1) + l * h1
            return 2 * schräge_wand + b * h1
        raise ValueError(f"Unbekannte Flächenart: {art}")

    def _parse_float(self, value) -> float:
        """
        Converts a value into a float, supporting both comma and dot as decimal separators.

        Args:
            value: Input value (string, int, float, or NaN).

        Returns:
            float: Parsed number. Returns 0.0 for empty or null values.

        Raises:
            ValueError: If the value cannot be parsed.
        """
        if pd.isnull(value) or value == "":
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        value = str(value).replace(",", ".")
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"Ungültige Zahl: '{value}'") from exc
