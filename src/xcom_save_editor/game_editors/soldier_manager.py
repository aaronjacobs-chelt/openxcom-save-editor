"""
Soldier manager for handling soldier/agent statistics in OpenXCom save files.
"""
from typing import Any, Dict, List, Optional, Tuple
from .base_manager import BaseManager


class Soldier:
    """Represents a soldier/agent."""
    
    STATS = ['tu', 'stamina', 'health', 'bravery', 'reactions', 'firing', 
             'throwing', 'strength', 'psiStrength', 'psiSkill', 'melee', 'mana']
    
    def __init__(self, soldier_data: Dict[str, Any], base_index: int, soldier_index: int):
        self.data = soldier_data
        self.base_index = base_index
        self.soldier_index = soldier_index
    
    @property
    def name(self) -> str:
        return self.data.get('name', f'Soldier {self.soldier_index + 1}')
    
    @property
    def rank(self) -> int:
        return self.data.get('rank', 0)
    
    @property
    def missions(self) -> int:
        return self.data.get('missions', 0)
    
    @property
    def kills(self) -> int:
        return self.data.get('kills', 0)
    
    @property
    def current_stats(self) -> Dict[str, int]:
        return self.data.get('currentStats', {})
    
    @property
    def initial_stats(self) -> Dict[str, int]:
        return self.data.get('initialStats', {})
    
    def get_stat(self, stat_name: str) -> int:
        """Get current value of a specific stat."""
        return self.current_stats.get(stat_name, 0)
    
    def get_initial_stat(self, stat_name: str) -> int:
        """Get initial value of a specific stat."""
        return self.initial_stats.get(stat_name, 0)
    
    def __str__(self) -> str:
        return f"{self.name} (Rank {self.rank}, {self.missions} missions)"


class SoldierManager(BaseManager):
    """Manages soldiers/agents across all bases."""
    
    def get_all_soldiers(self) -> List[Soldier]:
        """Get all soldiers from all bases."""
        soldiers = []
        bases = self.get_current_value('bases')
        
        if not isinstance(bases, list):
            return soldiers
        
        for base_index, base in enumerate(bases):
            if not isinstance(base, dict) or 'soldiers' not in base:
                continue
            
            soldier_list = base['soldiers']
            if not isinstance(soldier_list, list):
                continue
            
            for soldier_index, soldier_data in enumerate(soldier_list):
                if isinstance(soldier_data, dict):
                    soldier = Soldier(soldier_data, base_index, soldier_index)
                    soldiers.append(soldier)
        
        return soldiers
    
    def get_soldiers_by_base(self, base_index: int) -> List[Soldier]:
        """Get soldiers for a specific base."""
        all_soldiers = self.get_all_soldiers()
        return [soldier for soldier in all_soldiers if soldier.base_index == base_index]
    
    def set_soldier_stat(self, soldier: Soldier, stat_name: str, value: int) -> None:
        """
        Set a specific stat for a soldier.
        
        Args:
            soldier: The soldier to modify
            stat_name: Name of the stat to change
            value: New value for the stat
        """
        if stat_name not in Soldier.STATS:
            raise ValueError(f"Invalid stat name: {stat_name}")
        
        if value < 0 or value > 255:  # OpenXCom uses 8-bit values typically
            raise ValueError(f"Stat value must be between 0 and 255")
        
        stat_path = f"bases.{soldier.base_index}.soldiers.{soldier.soldier_index}.currentStats.{stat_name}"
        self.set_value(stat_path, value)
    
    def set_soldier_stats(self, soldier: Soldier, stats: Dict[str, int]) -> None:
        """
        Set multiple stats for a soldier.
        
        Args:
            soldier: The soldier to modify
            stats: Dictionary of stat_name -> value
        """
        for stat_name, value in stats.items():
            self.set_soldier_stat(soldier, stat_name, value)
    
    def set_soldier_stats_to_max(self, soldier: Soldier, max_value: int = 100) -> None:
        """
        Set all soldier stats to maximum value.
        
        Args:
            soldier: The soldier to modify
            max_value: Maximum value for all stats (default 100)
        """
        max_value = max(1, min(255, max_value))  # Clamp between 1 and 255
        
        stats_to_set = {}
        for stat_name in Soldier.STATS:
            stats_to_set[stat_name] = max_value
        
        self.set_soldier_stats(soldier, stats_to_set)
    
    def set_all_soldiers_stats_to_max(self, max_value: int = 100) -> int:
        """
        Set all soldiers' stats to maximum value.
        
        Args:
            max_value: Maximum value for all stats
            
        Returns:
            Number of soldiers modified
        """
        soldiers = self.get_all_soldiers()
        
        for soldier in soldiers:
            self.set_soldier_stats_to_max(soldier, max_value)
        
        return len(soldiers)
    
    def set_base_soldiers_stats_to_max(self, base_index: int, max_value: int = 100) -> int:
        """
        Set all soldiers in a base to max stats.
        
        Args:
            base_index: Index of the base
            max_value: Maximum value for all stats
            
        Returns:
            Number of soldiers modified
        """
        soldiers = self.get_soldiers_by_base(base_index)
        
        for soldier in soldiers:
            self.set_soldier_stats_to_max(soldier, max_value)
        
        return len(soldiers)
    
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
    
    def get_soldier_summary(self) -> Dict[str, Any]:
        """Get a summary of soldier status across all bases."""
        all_soldiers = self.get_all_soldiers()
        base_names = self.get_base_names()
        base_summaries = []
        
        for i, base_name in enumerate(base_names):
            base_soldiers = self.get_soldiers_by_base(i)
            
            base_summaries.append({
                'name': base_name,
                'soldier_count': len(base_soldiers),
                'soldiers': [
                    {
                        'name': soldier.name,
                        'rank': soldier.rank,
                        'missions': soldier.missions,
                        'kills': soldier.kills
                    }
                    for soldier in base_soldiers
                ]
            })
        
        return {
            'total_soldiers': len(all_soldiers),
            'bases': base_summaries
        }
    
    def get_stat_ranges_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of stat ranges across all soldiers."""
        soldiers = self.get_all_soldiers()
        
        if not soldiers:
            return {}
        
        stat_summary = {}
        
        for stat_name in Soldier.STATS:
            values = []
            for soldier in soldiers:
                stat_value = soldier.get_stat(stat_name)
                if stat_value > 0:  # Only include non-zero values
                    values.append(stat_value)
            
            if values:
                stat_summary[stat_name] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }
        
        return stat_summary
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of changes made to soldiers."""
        if not self.has_changes():
            return {'modified': {}, 'added': {}, 'removed': {}}
        
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # Compare original and current soldier states
        original_soldiers = SoldierManager(self.original_data).get_all_soldiers()
        current_soldiers = self.get_all_soldiers()
        
        modified_count = 0
        for current_soldier in current_soldiers:
            # Find corresponding original soldier
            original_soldier = None
            for orig_soldier in original_soldiers:
                if (orig_soldier.base_index == current_soldier.base_index and 
                    orig_soldier.soldier_index == current_soldier.soldier_index):
                    original_soldier = orig_soldier
                    break
            
            if original_soldier:
                # Check if any stats changed
                stats_changed = False
                for stat_name in Soldier.STATS:
                    if (original_soldier.get_stat(stat_name) != 
                        current_soldier.get_stat(stat_name)):
                        stats_changed = True
                        break
                
                if stats_changed:
                    modified_count += 1
        
        if modified_count > 0:
            changes['modified']['soldier_stats'] = {
                'original': f"Original soldier statistics",
                'current': f"{modified_count} soldier(s) stats modified",
                'field': 'Soldier Statistics'
            }
        
        return changes