"""
Facility manager for handling base facility construction in OpenXCom save files.
"""
from typing import Any, Dict, List, Optional, Tuple
from .base_manager import BaseManager


class Facility:
    """Represents a base facility."""
    
    def __init__(self, facility_data: Dict[str, Any], base_index: int, facility_index: int):
        self.data = facility_data
        self.base_index = base_index
        self.facility_index = facility_index
    
    @property
    def type(self) -> str:
        return self.data.get('type', 'Unknown Facility')
    
    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        name = self.type.replace('STR_', '').replace('_', ' ')
        return name.title()
    
    @property
    def x(self) -> int:
        return self.data.get('x', 0)
    
    @property
    def y(self) -> int:
        return self.data.get('y', 0)
    
    @property
    def build_time_remaining(self) -> Optional[int]:
        return self.data.get('buildTime')
    
    @property
    def is_under_construction(self) -> bool:
        return self.build_time_remaining is not None and self.build_time_remaining > 0
    
    @property
    def is_completed(self) -> bool:
        return not self.is_under_construction
    
    def __str__(self) -> str:
        if self.is_under_construction:
            return f"{self.display_name} (Building: {self.build_time_remaining} hours left)"
        else:
            return f"{self.display_name} (Complete)"


class FacilityManager(BaseManager):
    """Manages base facilities across all bases."""
    
    def get_all_facilities(self) -> List[Facility]:
        """Get all facilities from all bases."""
        facilities = []
        bases = self.get_current_value('bases')
        
        if not isinstance(bases, list):
            return facilities
        
        for base_index, base in enumerate(bases):
            if not isinstance(base, dict) or 'facilities' not in base:
                continue
            
            facility_list = base['facilities']
            if not isinstance(facility_list, list):
                continue
            
            for facility_index, facility_data in enumerate(facility_list):
                if isinstance(facility_data, dict):
                    facility = Facility(facility_data, base_index, facility_index)
                    facilities.append(facility)
        
        return facilities
    
    def get_facilities_by_base(self, base_index: int) -> List[Facility]:
        """Get facilities for a specific base."""
        all_facilities = self.get_all_facilities()
        return [facility for facility in all_facilities if facility.base_index == base_index]
    
    def get_facilities_under_construction(self) -> List[Facility]:
        """Get all facilities currently under construction."""
        return [facility for facility in self.get_all_facilities() if facility.is_under_construction]
    
    def get_completed_facilities(self) -> List[Facility]:
        """Get all completed facilities."""
        return [facility for facility in self.get_all_facilities() if facility.is_completed]
    
    def complete_facility_construction(self, facility: Facility) -> None:
        """
        Complete construction of a specific facility.
        
        Args:
            facility: The facility to complete
        """
        if not facility.is_under_construction:
            return  # Already completed
        
        facility_path = f"bases.{facility.base_index}.facilities.{facility.facility_index}"
        
        # Remove the buildTime field to mark as complete
        current_data = self.get_current_value(facility_path)
        if isinstance(current_data, dict) and 'buildTime' in current_data:
            # Create a copy without buildTime
            new_data = {k: v for k, v in current_data.items() if k != 'buildTime'}
            self.set_value(facility_path, new_data)
    
    def complete_all_facility_construction(self) -> int:
        """
        Complete construction of all facilities under construction.
        
        Returns:
            Number of facilities completed
        """
        facilities_under_construction = self.get_facilities_under_construction()
        
        for facility in facilities_under_construction:
            self.complete_facility_construction(facility)
        
        return len(facilities_under_construction)
    
    def complete_base_facility_construction(self, base_index: int) -> int:
        """
        Complete construction of all facilities in a specific base.
        
        Args:
            base_index: Index of the base
            
        Returns:
            Number of facilities completed
        """
        base_facilities = self.get_facilities_by_base(base_index)
        facilities_under_construction = [f for f in base_facilities if f.is_under_construction]
        
        for facility in facilities_under_construction:
            self.complete_facility_construction(facility)
        
        return len(facilities_under_construction)
    
    def set_facility_build_time(self, facility: Facility, hours: int) -> None:
        """
        Set build time for a facility.
        
        Args:
            facility: The facility to modify
            hours: Build time in hours (0 to complete immediately)
        """
        facility_path = f"bases.{facility.base_index}.facilities.{facility.facility_index}"
        
        if hours <= 0:
            # Complete the facility
            self.complete_facility_construction(facility)
        else:
            # Set build time
            current_data = self.get_current_value(facility_path)
            if isinstance(current_data, dict):
                current_data['buildTime'] = hours
                self.set_value(facility_path, current_data)
    
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
    
    def get_facility_summary(self) -> Dict[str, Any]:
        """Get a summary of facility status across all bases."""
        all_facilities = self.get_all_facilities()
        facilities_under_construction = self.get_facilities_under_construction()
        
        base_names = self.get_base_names()
        base_summaries = []
        
        for i, base_name in enumerate(base_names):
            base_facilities = self.get_facilities_by_base(i)
            base_under_construction = [f for f in base_facilities if f.is_under_construction]
            
            base_summaries.append({
                'name': base_name,
                'total_facilities': len(base_facilities),
                'under_construction': len(base_under_construction),
                'completed': len(base_facilities) - len(base_under_construction),
                'facilities_building': [
                    {
                        'name': facility.display_name,
                        'time_remaining': facility.build_time_remaining,
                        'position': f"({facility.x}, {facility.y})"
                    }
                    for facility in base_under_construction
                ]
            })
        
        return {
            'total_facilities': len(all_facilities),
            'under_construction': len(facilities_under_construction),
            'completed': len(all_facilities) - len(facilities_under_construction),
            'bases': base_summaries
        }
    
    def get_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of changes made to facilities."""
        if not self.has_changes():
            return {'modified': {}, 'added': {}, 'removed': {}}
        
        changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # Compare original and current facility states
        original_facilities = FacilityManager(self.original_data).get_facilities_under_construction()
        current_facilities = self.get_facilities_under_construction()
        
        completed_count = len(original_facilities) - len(current_facilities)
        
        if completed_count > 0:
            changes['modified']['facilities_completed'] = {
                'original': f"{len(original_facilities)} facilities under construction",
                'current': f"{completed_count} facility construction(s) completed",
                'field': 'Facility Construction'
            }
        
        return changes