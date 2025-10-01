"""
Production manager for handling manufacturing queues in OpenXCom save files.
"""
from typing import Any, Dict, List, Optional, Tuple
from .base_manager import BaseManager


class ProductionItem:
    """Represents a production/manufacturing item."""
    
    def __init__(self, production_data: Dict[str, Any], base_index: int, production_index: int):
        self.data = production_data
        self.base_index = base_index
        self.production_index = production_index
    
    @property
    def item_type(self) -> str:
        return self.data.get('item', 'Unknown Item')
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        name = self.item_type.replace('STR_', '').replace('_', ' ')
        return name.title()
    
    @property
    def assigned_engineers(self) -> int:
        return self.data.get('assigned', 0)
    
    @property
    def time_spent(self) -> int:
        return self.data.get('spent', 0)
    
    @property
    def amount_to_produce(self) -> int:
        return self.data.get('amount', 1)
    
    @property
    def is_infinite(self) -> bool:
        return self.data.get('infinite', False)
    
    @property
    def is_completed(self) -> bool:
        # For infinite production, never completed
        if self.is_infinite:
            return False
        
        # Calculate if enough time has been spent based on amount
        # This is simplified - actual calculation would depend on item production cost
        # For now, we'll assume if spent time > 0 and amount > 0, it's being worked on
        return self.time_spent > 0 and self.amount_to_produce <= 1
    
    def __str__(self) -> str:
        if self.is_infinite:
            return f"{self.display_name} (Infinite production, {self.time_spent} hours spent)"
        else:
            return f"{self.display_name} x{self.amount_to_produce} ({self.time_spent} hours spent)"


class ProductionManager(BaseManager):
    """Manages production/manufacturing across all bases."""
    
    def get_all_production_items(self) -> List[ProductionItem]:
        """Get all production items from all bases."""
        items = []
        bases = self.get_current_value('bases')
        
        if not isinstance(bases, list):
            return items
        
        for base_index, base in enumerate(bases):
            if not isinstance(base, dict) or 'productions' not in base:
                continue
            
            production_list = base['productions']
            if not isinstance(production_list, list):
                continue
            
            for production_index, production_data in enumerate(production_list):
                if isinstance(production_data, dict):
                    item = ProductionItem(production_data, base_index, production_index)
                    items.append(item)
        
        return items
    
    def get_production_by_base(self, base_index: int) -> List[ProductionItem]:
        """Get production items for a specific base."""
        all_items = self.get_all_production_items()
        return [item for item in all_items if item.base_index == base_index]
    
    def get_active_production_items(self) -> List[ProductionItem]:
        """Get production items that are currently being worked on."""
        return [item for item in self.get_all_production_items() 
                if item.assigned_engineers > 0 or item.time_spent > 0]
    
    def complete_production_item(self, item: ProductionItem) -> None:
        """
        Complete production of a specific item by setting spent time high enough.
        
        Args:
            item: The production item to complete
        """
        if item.is_infinite:
            # For infinite items, we can't really "complete" them
            # Instead, we'll set spent time to a high value to indicate completion of current batch
            completion_time = max(100, item.time_spent + 50)
        else:
            # For regular items, set spent time to a value that would complete production
            # This is simplified - in reality we'd need to know the actual production cost
            completion_time = max(item.time_spent + item.amount_to_produce * 10, 100)
        
        item_path = f"bases.{item.base_index}.productions.{item.production_index}.spent"
        self.set_value(item_path, completion_time)
    
    def complete_all_production_items(self) -> int:
        """
        Complete all active production items.
        
        Returns:
            Number of items completed
        """
        active_items = self.get_active_production_items()
        
        for item in active_items:
            self.complete_production_item(item)
        
        return len(active_items)
    
    def complete_base_production_items(self, base_index: int) -> int:
        """
        Complete all production items in a specific base.
        
        Args:
            base_index: Index of the base
            
        Returns:
            Number of items completed
        """
        base_items = self.get_production_by_base(base_index)
        active_items = [item for item in base_items if item.assigned_engineers > 0 or item.time_spent > 0]
        
        for item in active_items:
            self.complete_production_item(item)
        
        return len(active_items)
    
    def set_production_progress(self, item: ProductionItem, hours: int) -> None:
        """
        Set production progress to a specific number of hours.
        
        Args:
            item: The production item
            hours: Hours of work completed
        """
        hours = max(0, hours)
        
        item_path = f"bases.{item.base_index}.productions.{item.production_index}.spent"
        self.set_value(item_path, hours)
    
    def set_production_amount(self, item: ProductionItem, amount: int) -> None:
        """
        Set the amount to produce for an item.
        
        Args:
            item: The production item
            amount: New amount to produce
        """
        if amount < 1:
            raise ValueError("Production amount must be at least 1")
        
        item_path = f"bases.{item.base_index}.productions.{item.production_index}.amount"
        self.set_value(item_path, amount)
    
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
    
    def get_production_summary(self) -> Dict[str, Any]:
        """Get a summary of production status across all bases."""
        all_items = self.get_all_production_items()
        active_items = self.get_active_production_items()
        
        base_names = self.get_base_names()
        base_summaries = []
        
        for i, base_name in enumerate(base_names):
            base_items = self.get_production_by_base(i)
            base_active = [item for item in base_items if item.assigned_engineers > 0 or item.time_spent > 0]
            
            base_summaries.append({
                'name': base_name,
                'total_production_items': len(base_items),
                'active_items': len(base_active),
                'items_in_queue': [
                    {
                        'name': item.display_name,
                        'amount': item.amount_to_produce,
                        'time_spent': item.time_spent,
                        'engineers': item.assigned_engineers,
                        'infinite': item.is_infinite
                    }
                    for item in base_active
                ]
            })
        
        return {
            'total_production_items': len(all_items),
            'active_items': len(active_items),
            'bases': base_summaries
        }
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of changes made to production."""
        if not self.has_changes():
            return {'modified': {}, 'added': {}, 'removed': {}}
        
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # Compare original and current production states
        original_items = ProductionManager(self.original_data).get_all_production_items()
        current_items = self.get_all_production_items()
        
        modified_count = 0
        for current_item in current_items:
            # Find corresponding original item
            original_item = None
            for orig_item in original_items:
                if (orig_item.base_index == current_item.base_index and 
                    orig_item.production_index == current_item.production_index):
                    original_item = orig_item
                    break
            
            if original_item and original_item.time_spent != current_item.time_spent:
                modified_count += 1
        
        if modified_count > 0:
            changes['modified']['production_progress'] = {
                'original': f"Original production progress",
                'current': f"{modified_count} production item(s) modified",
                'field': 'Production Progress'
            }
        
        return changes