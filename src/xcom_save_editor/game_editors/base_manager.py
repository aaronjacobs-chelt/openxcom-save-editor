"""
Base manager class providing common functionality for all save game data managers.
Handles snapshot management and change tracking.
"""
import copy
from typing import Any, Dict, List, Optional


class BaseManager:
    """Base class for all save game data managers."""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize manager with save game data.
        
        Args:
            data: The full save game data dictionary
        """
        self.original_data = copy.deepcopy(data)
        self.current_data = data
        self.changes_made = False
    
    def get_original_value(self, key_path: str) -> Any:
        """
        Get original value at the specified key path.
        
        Args:
            key_path: Dot-separated path to the value (e.g., "bases.0.name")
        """
        return self._get_nested_value(self.original_data, key_path)
    
    def get_current_value(self, key_path: str) -> Any:
        """
        Get current value at the specified key path.
        
        Args:
            key_path: Dot-separated path to the value
        """
        return self._get_nested_value(self.current_data, key_path)
    
    def set_value(self, key_path: str, value: Any) -> None:
        """
        Set value at the specified key path.
        
        Args:
            key_path: Dot-separated path to the value
            value: New value to set
        """
        self._set_nested_value(self.current_data, key_path, value)
        self.changes_made = True
    
    def has_changes(self) -> bool:
        """Check if any changes have been made."""
        return self.changes_made
    
    def reset_changes(self) -> None:
        """Reset all changes to original state."""
        self.current_data = copy.deepcopy(self.original_data)
        self.changes_made = False
    
    def update_original_data(self, new_data: Dict[str, Any]) -> None:
        """Update original data after successful save and reset change tracking.
        
        Args:
            new_data: The updated data dictionary
        """
        self.original_data = copy.deepcopy(new_data)
        self.current_data = new_data
        self.changes_made = False
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a summary of all changes made.
        
        Returns:
            Dict with 'added', 'modified', 'removed' keys containing change details
        """
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # This is a simplified implementation - more complex change detection
        # could be implemented in subclasses
        if self.changes_made:
            changes['modified']['data'] = {
                'original': 'Original data (complex structure)',
                'current': 'Modified data (complex structure)'
            }
        
        return changes
    
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                if key in current:
                    current = current[key]
                else:
                    return None
            elif isinstance(current, list):
                try:
                    index = int(key)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                except ValueError:
                    return None
            else:
                return None
        
        return current
    
    def _set_nested_value(self, data: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation."""
        keys = key_path.split('.')
        current = data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if isinstance(current, dict):
                if key not in current:
                    current[key] = {}
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        raise IndexError(f"List index {index} out of range")
                except ValueError:
                    raise ValueError(f"Invalid list index: {key}")
            else:
                raise ValueError(f"Cannot navigate into {type(current)} with key {key}")
        
        # Set the final value
        final_key = keys[-1]
        if isinstance(current, dict):
            current[final_key] = value
        elif isinstance(current, list):
            try:
                index = int(final_key)
                if 0 <= index < len(current):
                    current[index] = value
                else:
                    raise IndexError(f"List index {index} out of range")
            except ValueError:
                raise ValueError(f"Invalid list index: {final_key}")
        else:
            raise ValueError(f"Cannot set value in {type(current)}")
    
    def _find_items_by_condition(self, items: List[Dict], condition_func) -> List[int]:
        """
        Find items in a list that match a condition.
        
        Args:
            items: List of dictionaries to search
            condition_func: Function that returns True for matching items
            
        Returns:
            List of indices of matching items
        """
        return [i for i, item in enumerate(items) if condition_func(item)]
    
    def _format_item_name(self, item_name: str) -> str:
        """Format OpenXCom item names for display."""
        # Remove STR_ prefix and replace underscores with spaces
        formatted = item_name.replace('STR_', '').replace('_', ' ')
        return formatted.title()