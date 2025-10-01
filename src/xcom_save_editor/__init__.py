"""
OpenXCom Save Editor

A tool for editing OpenXCom save files, specifically designed for the X-Com Files mod.
Provides safe editing of money, research, soldiers, facilities, production, and inventory.
"""

__version__ = "1.0.0"
__author__ = "OpenXCom Save Editor"
__description__ = "A safe save editor for OpenXCom games with X-Com Files mod support"

from .editor import OpenXComSaveEditor
from .cli import SaveEditorCLI

__all__ = ["OpenXComSaveEditor", "SaveEditorCLI"]