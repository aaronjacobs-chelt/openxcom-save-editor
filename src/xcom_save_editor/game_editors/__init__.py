"""
Game editors package for OpenXCom save file modification.
Contains managers for different aspects of the save game.
"""

from .base_manager import BaseManager
from .money_manager import MoneyManager
from .research_manager import ResearchManager
from .soldier_manager import SoldierManager
from .facility_manager import FacilityManager
from .production_manager import ProductionManager
from .inventory_manager import InventoryManager

__all__ = [
    'BaseManager',
    'MoneyManager',
    'ResearchManager',
    'SoldierManager',
    'FacilityManager',
    'ProductionManager',
    'InventoryManager'
]