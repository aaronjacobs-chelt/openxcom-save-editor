"""
Inventory manager for handling base item storage in OpenXCom save files.
"""
from typing import Any, Dict, List, Optional, Tuple
from .base_manager import BaseManager


class InventoryManager(BaseManager):
    """Manages inventory/items across all bases."""
    
    def get_all_base_inventories(self) -> Dict[int, Dict[str, int]]:
        """Get inventory for all bases."""
        inventories = {}
        bases = self.get_current_value('bases')
        
        if not isinstance(bases, list):
            return inventories
        
        for base_index, base in enumerate(bases):
            if not isinstance(base, dict) or 'items' not in base:
                inventories[base_index] = {}
                continue
            
            items = base['items']
            if isinstance(items, dict):
                inventories[base_index] = items.copy()
            else:
                inventories[base_index] = {}
        
        return inventories
    
    def get_base_inventory(self, base_index: int) -> Dict[str, int]:
        """Get inventory for a specific base."""
        inventories = self.get_all_base_inventories()
        return inventories.get(base_index, {})
    
    def get_item_quantity(self, base_index: int, item_name: str) -> int:
        """Get quantity of a specific item in a base."""
        inventory = self.get_base_inventory(base_index)
        return inventory.get(item_name, 0)
    
    def set_item_quantity(self, base_index: int, item_name: str, quantity: int) -> None:
        """
        Set quantity of a specific item in a base.
        
        Args:
            base_index: Index of the base
            item_name: Name of the item (e.g., 'STR_GLOCK_18')
            quantity: New quantity (0 to remove item)
        """
        if quantity < 0:
            raise ValueError("Item quantity cannot be negative")
        
        item_path = f"bases.{base_index}.items.{item_name}"
        
        if quantity == 0:
            # Remove the item by getting the current items dict and removing the key
            current_items = self.get_base_inventory(base_index)
            if item_name in current_items:
                del current_items[item_name]
                self.set_value(f"bases.{base_index}.items", current_items)
        else:
            self.set_value(item_path, quantity)
    
    def add_item(self, base_index: int, item_name: str, quantity: int = 1) -> None:
        """
        Add items to a base inventory.
        
        Args:
            base_index: Index of the base
            item_name: Name of the item
            quantity: Quantity to add
        """
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive")
        
        current_quantity = self.get_item_quantity(base_index, item_name)
        new_quantity = current_quantity + quantity
        self.set_item_quantity(base_index, item_name, new_quantity)
    
    def remove_item(self, base_index: int, item_name: str, quantity: int = None) -> None:
        """
        Remove items from a base inventory.
        
        Args:
            base_index: Index of the base
            item_name: Name of the item
            quantity: Quantity to remove (None to remove all)
        """
        if quantity is None:
            # Remove all
            self.set_item_quantity(base_index, item_name, 0)
        else:
            if quantity <= 0:
                raise ValueError("Quantity to remove must be positive")
            
            current_quantity = self.get_item_quantity(base_index, item_name)
            new_quantity = max(0, current_quantity - quantity)
            self.set_item_quantity(base_index, item_name, new_quantity)
    
    def get_all_unique_items(self) -> List[str]:
        """Get a list of all unique item types across all bases."""
        unique_items = set()
        inventories = self.get_all_base_inventories()
        
        for inventory in inventories.values():
            unique_items.update(inventory.keys())
        
        return sorted(list(unique_items))
    
    def get_item_totals(self) -> Dict[str, int]:
        """Get total quantities of all items across all bases."""
        totals = {}
        inventories = self.get_all_base_inventories()
        
        for inventory in inventories.values():
            for item_name, quantity in inventory.items():
                if item_name in totals:
                    totals[item_name] += quantity
                else:
                    totals[item_name] = quantity
        
        return totals
    
    def search_items(self, search_term: str) -> Dict[str, int]:
        """
        Search for items by name.
        
        Args:
            search_term: Term to search for in item names
            
        Returns:
            Dictionary of matching items and their total quantities
        """
        search_term = search_term.lower()
        totals = self.get_item_totals()
        
        matching_items = {}
        for item_name, total_quantity in totals.items():
            # Search in both original name and formatted name
            formatted_name = self._format_item_name(item_name).lower()
            if search_term in item_name.lower() or search_term in formatted_name:
                matching_items[item_name] = total_quantity
        
        return matching_items
    
    def get_base_names(self) -> List[str]:
        """Get names of all bases."""
        bases = self.get_current_value('bases')
        if not isinstance(bases, list):
            return []
        
        names = []
        for i, base in enumerate(bases):
            if isinstance(base, dict) and 'name' in base:
                names.append(base['name'])
            else:
                names.append(f"Base {i + 1}")
        
        return names
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Get a summary of inventory status across all bases."""
        inventories = self.get_all_base_inventories()
        base_names = self.get_base_names()
        all_unique_items = self.get_all_unique_items()
        item_totals = self.get_item_totals()
        
        base_summaries = []
        for i, base_name in enumerate(base_names):
            inventory = inventories.get(i, {})
            
            # Sort items by quantity (descending) for better display
            sorted_items = sorted(inventory.items(), key=lambda x: x[1], reverse=True)
            
            base_summaries.append({
                'name': base_name,
                'total_item_types': len(inventory),
                'total_items': sum(inventory.values()),
                'items': [
                    {
                        'name': item_name,
                        'display_name': self._format_item_name(item_name),
                        'quantity': quantity
                    }
                    for item_name, quantity in sorted_items
                ]
            })
        
        # Get top items across all bases
        sorted_totals = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)
        top_items = [
            {
                'name': item_name,
                'display_name': self._format_item_name(item_name),
                'total_quantity': quantity
            }
            for item_name, quantity in sorted_totals[:10]  # Top 10 items
        ]
        
        return {
            'total_unique_items': len(all_unique_items),
            'total_items_across_all_bases': sum(item_totals.values()),
            'top_items': top_items,
            'bases': base_summaries
        }
    
    def bulk_modify_items(self, base_index: int, item_modifications: Dict[str, int]) -> int:
        """
        Modify multiple items at once.
        
        Args:
            base_index: Index of the base
            item_modifications: Dictionary of item_name -> new_quantity
            
        Returns:
            Number of items modified
        """
        for item_name, quantity in item_modifications.items():
            self.set_item_quantity(base_index, item_name, quantity)
        
        return len(item_modifications)
    
    def copy_inventory_between_bases(self, source_base: int, target_base: int, 
                                   copy_mode: str = 'add') -> int:
        """
        Copy inventory from one base to another.
        
        Args:
            source_base: Index of source base
            target_base: Index of target base
            copy_mode: 'replace', 'add', or 'merge'
            
        Returns:
            Number of item types copied
        """
        source_inventory = self.get_base_inventory(source_base)
        
        if copy_mode == 'replace':
            # Replace entire inventory
            self.set_value(f"bases.{target_base}.items", source_inventory.copy())
            return len(source_inventory)
        
        elif copy_mode == 'add':
            # Add to existing inventory
            target_inventory = self.get_base_inventory(target_base)
            for item_name, quantity in source_inventory.items():
                current_quantity = target_inventory.get(item_name, 0)
                self.set_item_quantity(target_base, item_name, current_quantity + quantity)
            return len(source_inventory)
        
        elif copy_mode == 'merge':
            # Take maximum of both inventories
            target_inventory = self.get_base_inventory(target_base)
            all_items = set(source_inventory.keys()) | set(target_inventory.keys())
            
            for item_name in all_items:
                source_qty = source_inventory.get(item_name, 0)
                target_qty = target_inventory.get(item_name, 0)
                max_qty = max(source_qty, target_qty)
                self.set_item_quantity(target_base, item_name, max_qty)
            
            return len(all_items)
        
        else:
            raise ValueError(f"Invalid copy_mode: {copy_mode}")
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of changes made to inventory."""
        if not self.has_changes():
            return {'modified': {}, 'added': {}, 'removed': {}}
        
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # Compare original and current inventories
        original_inventories = InventoryManager(self.original_data).get_all_base_inventories()
        current_inventories = self.get_all_base_inventories()
        
        modified_bases = 0
        total_changes = 0
        
        for base_index in current_inventories.keys():
            original_inv = original_inventories.get(base_index, {})
            current_inv = current_inventories.get(base_index, {})
            
            if original_inv != current_inv:
                modified_bases += 1
                
                # Count individual item changes
                all_items = set(original_inv.keys()) | set(current_inv.keys())
                for item in all_items:
                    if original_inv.get(item, 0) != current_inv.get(item, 0):
                        total_changes += 1
        
        if total_changes > 0:
            changes['modified']['inventory_items'] = {
                'original': f"Original inventory",
                'current': f"{total_changes} item quantities changed in {modified_bases} base(s)",
                'field': 'Base Inventory'
            }
        
        return changes