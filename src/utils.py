"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""
import os
import sys


def resource_path(relative_path, base_dir=None):
    """
    Returns the absolute path to a resource, depending on whether the app
    is running in a development context or as a PyInstaller bundle.
    `base_dir` is optional and can be used to define a custom base directory.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller: 'frozen' attribute is set
        base_path = sys._MEIPASS
    else:
        # Development: use provided base_dir or current directory
        base_path = base_dir or os.path.abspath(".")

    return os.path.join(base_path, relative_path)
