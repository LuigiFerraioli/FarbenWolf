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
        """Sets customer data for export"""
        pass

    @abstractmethod
    def create_file(self, df: pd.DataFrame, filename: Optional[str] = None) -> None:
        """Creates a file based on the provided DataFrame"""
        pass

    @abstractmethod
    def build_filename(self, customer_data: dict, base_name: str = "report") -> str:
        """Generates a filename based on customer information and configuration"""
        pass

    @abstractmethod
    def append_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """Appends units to the column headers of the DataFrame."""
        pass
