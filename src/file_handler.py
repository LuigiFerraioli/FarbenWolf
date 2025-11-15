"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class IFileHandler(ABC):
    """
    Interface for all file generators (PDF, Excel, etc.)
    """

    @abstractmethod
    def set_customer_data(self, data: dict) -> None:
        """
        Sets the customer data for export.

        Args:
            data (dict): A dictionary containing customer information 
                         (e.g., name, ID, contact details, etc.).
        """
        pass

    @abstractmethod
    def create_file(self, df: pd.DataFrame, filename: Optional[str] = None) -> None:
        """Creates a file based on the provided DataFrame"""
        pass

    @abstractmethod
    def build_filename(self, customer_data: dict, base_name: str = "report") -> str:
        """
        Constructs a filename based on configuration flags and customer data.

        This method must return a filename including the appropriate extension (e.g., .pdf or .xlsx),
        combining elements like customer name, date, and time according to configuration.

        Args:
            customer_data (Dict[str, str]): Dictionary containing customer information 
                                            (e.g., 'Vorname', 'Nachname').
            base_name (str, optional): Default fallback name if no specific parts are configured. Defaults to "bericht".

        Returns:
            str: Constructed filename ready for saving.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def set_save_path(self, path: str) -> None:
        """
        Sets the directory where files will be saved.

        Args:
            path (str): Directory path for saving files.

        Raises:
            ValueError: If the path is invalid.
        """
        pass
