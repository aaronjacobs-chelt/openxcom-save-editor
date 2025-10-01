"""
Main OpenXCom save game editor class.
Coordinates all managers and handles the editing workflow.
"""
import copy
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils.file_ops import SaveFileManager
from .utils.validator import detailed_validate_save
from .game_editors import (
    MoneyManager, ResearchManager, SoldierManager, 
    FacilityManager, ProductionManager, InventoryManager
)


class OpenXComSaveEditor:
    """Main save game editor that coordinates all functionality."""
    
    def __init__(self, save_file_path: str):
        """
        Initialize the save editor.
        
        Args:
            save_file_path: Path to the OpenXCom save file
        """
        self.save_file_path = Path(save_file_path)
        self.file_manager = SaveFileManager(str(self.save_file_path))
        
        # Load the save data
        self.save_data = self.file_manager.load_save_file()
        self.original_save_data = copy.deepcopy(self.save_data)
        
        # Initialize managers
        self.money_manager = MoneyManager(self.save_data)
        self.research_manager = ResearchManager(self.save_data)
        self.soldier_manager = SoldierManager(self.save_data)
        self.facility_manager = FacilityManager(self.save_data)
        self.production_manager = ProductionManager(self.save_data)
        self.inventory_manager = InventoryManager(self.save_data)
        
        # Track if backup was created
        self.backup_created = False
        self.backup_path = None
    
    def create_backup(self) -> str:
        """Create a backup of the save file."""
        if not self.backup_created:
            self.backup_path = self.file_manager.create_backup()
            self.backup_created = True
        return self.backup_path
    
    def get_save_info(self) -> Dict[str, Any]:
        """Get information about the current save file."""
        file_info = self.file_manager.get_file_info()
        
        # Get header data from first YAML document, fall back to main save data
        header = self.file_manager.header_data or {}
        
        # Add game-specific information
        save_info = {
            **file_info,
            'save_name': header.get('name', self.save_data.get('name', 'Unknown')),
            'game_version': header.get('version', self.save_data.get('version', 'Unknown')),
            'game_engine': header.get('engine', self.save_data.get('engine', 'Unknown')),
            'difficulty': self.save_data.get('difficulty', 0),
            'months_passed': self.save_data.get('monthsPassed', 0),
            'days_passed': self.save_data.get('daysPassed', 0),
        }
        
        # Add base information
        bases = self.save_data.get('bases', [])
        save_info['total_bases'] = len(bases)
        save_info['base_names'] = []
        
        for i, base in enumerate(bases):
            if isinstance(base, dict):
                name = base.get('name', f'Base {i + 1}')
                save_info['base_names'].append(name)
        
        return save_info
    
    def has_changes(self) -> bool:
        """Check if any changes have been made."""
        return (self.money_manager.has_changes() or
                self.research_manager.has_changes() or
                self.soldier_manager.has_changes() or
                self.facility_manager.has_changes() or
                self.production_manager.has_changes() or
                self.inventory_manager.has_changes())
    
    def get_all_changes_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get a comprehensive summary of all changes made."""
        all_changes = {
            'modified': {},
            'added': {},
            'removed': {}
        }
        
        # Collect changes from all managers
        managers = [
            ('Money', self.money_manager),
            ('Research', self.research_manager),
            ('Soldiers', self.soldier_manager),
            ('Facilities', self.facility_manager),
            ('Production', self.production_manager),
            ('Inventory', self.inventory_manager)
        ]
        
        for manager_name, manager in managers:
            changes = manager.get_changes_summary()
            
            for change_type in ['modified', 'added', 'removed']:
                if changes[change_type]:
                    for key, value in changes[change_type].items():
                        all_changes[change_type][f"{manager_name}_{key}"] = value
        
        return all_changes
    
    def reset_all_changes(self) -> None:
        """Reset all changes to original state."""
        # Reset the main save data
        self.save_data = copy.deepcopy(self.original_save_data)
        
        # Reinitialize all managers with the reset data
        self.money_manager = MoneyManager(self.save_data)
        self.research_manager = ResearchManager(self.save_data)
        self.soldier_manager = SoldierManager(self.save_data)
        self.facility_manager = FacilityManager(self.save_data)
        self.production_manager = ProductionManager(self.save_data)
        self.inventory_manager = InventoryManager(self.save_data)
    
    def validate_save_data(self) -> tuple[bool, List[str], List[str]]:
        """Validate the current save data."""
        return detailed_validate_save(self.save_data)
    
    def commit_changes(self, create_backup: bool = True) -> bool:
        """
        Save all changes to the file.
        
        Args:
            create_backup: Whether to create a backup before saving
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if requested
            if create_backup:
                self.create_backup()
            
            # Validate before saving
            is_valid, errors, warnings = self.validate_save_data()
            if not is_valid:
                raise ValueError(f"Save validation failed: {', '.join(errors)}")
            
            # Save the file
            self.file_manager.save_file(self.save_data)
            
            # Update original data to current state
            self.original_save_data = copy.deepcopy(self.save_data)
            
            # Reset change tracking in all managers
            self.money_manager.update_original_data(self.save_data)
            self.research_manager.update_original_data(self.save_data)
            self.soldier_manager.update_original_data(self.save_data)
            self.facility_manager.update_original_data(self.save_data)
            self.production_manager.update_original_data(self.save_data)
            self.inventory_manager.update_original_data(self.save_data)
            
            return True
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def restore_backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Restore from a backup file.
        
        Args:
            backup_path: Path to backup file (uses most recent if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if backup_path is None:
                # Use the most recent backup
                backups = self.file_manager.list_backups()
                if not backups:
                    print("No backups available")
                    return False
                backup_path = backups[0]  # Most recent
            
            # Restore the backup
            self.file_manager.restore_backup(backup_path)
            
            # Reload the data
            self.save_data = self.file_manager.load_save_file()
            self.original_save_data = copy.deepcopy(self.save_data)
            
            # Reinitialize managers
            self.money_manager = MoneyManager(self.save_data)
            self.research_manager = ResearchManager(self.save_data)
            self.soldier_manager = SoldierManager(self.save_data)
            self.facility_manager = FacilityManager(self.save_data)
            self.production_manager = ProductionManager(self.save_data)
            self.inventory_manager = InventoryManager(self.save_data)
            
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def get_available_backups(self) -> List[Dict[str, Any]]:
        """Get information about available backup files."""
        backup_paths = self.file_manager.list_backups()
        backups = []
        
        for backup_path in backup_paths:
            backup_file = Path(backup_path)
            if backup_file.exists():
                stat = backup_file.stat()
                backups.append({
                    'path': backup_path,
                    'name': backup_file.name,
                    'size': stat.st_size,
                    'created': stat.st_mtime,
                    'created_str': backup_file.stat().st_mtime  # Will be formatted in CLI
                })
        
        return backups
    
    # Convenience methods for common operations
    
    def quick_max_soldiers(self, max_value: int = 100) -> int:
        """Quick action: Set all soldiers to max stats."""
        return self.soldier_manager.set_all_soldiers_stats_to_max(max_value)
    
    def quick_complete_all_research(self) -> int:
        """Quick action: Complete all research projects."""
        return self.research_manager.complete_all_research_projects()
    
    def quick_complete_all_construction(self) -> int:
        """Quick action: Complete all facility construction."""
        return self.facility_manager.complete_all_facility_construction()
    
    def quick_complete_all_production(self) -> int:
        """Quick action: Complete all production items."""
        return self.production_manager.complete_all_production_items()
    
    def quick_set_money(self, amount: int) -> None:
        """Quick action: Set money to specified amount."""
        self.money_manager.set_current_month_funds(amount)
    
    def get_quick_status(self) -> Dict[str, Any]:
        """Get a quick overview of the save game status."""
        money = self.money_manager.get_funds_display()
        
        research_summary = self.research_manager.get_research_summary()
        facility_summary = self.facility_manager.get_facility_summary()
        production_summary = self.production_manager.get_production_summary()
        soldier_summary = self.soldier_manager.get_soldier_summary()
        
        return {
            'funds': {
                'current': money[0],
                'previous': money[1]
            },
            'research': {
                'active': research_summary['active_projects'],
                'completed': research_summary['completed_projects']
            },
            'facilities': {
                'building': facility_summary['under_construction'],
                'completed': facility_summary['completed']
            },
            'production': {
                'active': production_summary['active_items'],
                'total': production_summary['total_production_items']
            },
            'soldiers': {
                'total': soldier_summary['total_soldiers']
            },
            'bases': {
                'total': len(self.save_data.get('bases', [])),
                'names': [base.get('name', f'Base {i+1}') for i, base in enumerate(self.save_data.get('bases', []))]
            }
        }