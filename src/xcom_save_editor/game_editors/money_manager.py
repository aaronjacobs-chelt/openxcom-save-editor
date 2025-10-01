"""
Money manager for handling funds in OpenXCom save files.
"""
from typing import Any, Dict, List, Tuple
from .base_manager import BaseManager


class MoneyManager(BaseManager):
    """Manages money/funds in the save game."""
    
    def get_funds(self) -> List[int]:
        """
        Get current funds values.
        
        Returns:
            List of fund amounts [current_month, previous_month]
        """
        funds = self.get_current_value('funds')
        if not isinstance(funds, list) or len(funds) < 2:
            return [0, 0]
        return funds[:2]  # Only return first 2 values
    
    def get_funds_display(self) -> Tuple[int, int]:
        """
        Get funds formatted for display.
        
        Returns:
            Tuple of (current_month, previous_month)
        """
        funds = self.get_funds()
        return funds[0], funds[1]
    
    def set_funds(self, current_month: int, previous_month: int = None) -> None:
        """
        Set funds values.
        
        Args:
            current_month: Current month's funds
            previous_month: Previous month's funds (optional, defaults to current_month)
        """
        if previous_month is None:
            previous_month = current_month
        
        # Validate values
        if current_month < 0:
            raise ValueError("Current month funds cannot be negative")
        if previous_month < 0:
            raise ValueError("Previous month funds cannot be negative")
        
        funds = self.get_current_value('funds')
        if not isinstance(funds, list):
            funds = [0, 0]
        
        # Update first two values, keep any additional values unchanged
        funds[0] = current_month
        funds[1] = previous_month
        
        self.set_value('funds', funds)
    
    def set_current_month_funds(self, amount: int) -> None:
        """
        Set only the current month's funds.
        
        Args:
            amount: New amount for current month
        """
        if amount < 0:
            raise ValueError("Funds amount cannot be negative")
        
        current, previous = self.get_funds_display()
        self.set_funds(amount, previous)
    
    def add_funds(self, amount: int) -> None:
        """
        Add funds to the current month.
        
        Args:
            amount: Amount to add (can be negative to subtract)
        """
        current, previous = self.get_funds_display()
        new_amount = max(0, current + amount)  # Don't allow negative funds
        self.set_funds(new_amount, previous)
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of changes made to funds."""
        if not self.has_changes():
            return {'modified': {}, 'added': {}, 'removed': {}}
        
        original_funds = self.get_original_value('funds')
        current_funds = self.get_current_value('funds')
        
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        if original_funds != current_funds:
            changes['modified']['funds'] = {
                'original': f"Current: {original_funds[0]:,}, Previous: {original_funds[1]:,}",
                'current': f"Current: {current_funds[0]:,}, Previous: {current_funds[1]:,}",
                'field': 'Funds'
            }
        
        return changes