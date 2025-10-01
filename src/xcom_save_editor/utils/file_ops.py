"""
File operations utilities for OpenXCom save file management.
Handles YAML I/O, backups, and file restoration.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class SaveFileManager:
    """Manages save file operations including backup and restore functionality."""
    
    def __init__(self, save_path: str):
        self.save_path = Path(save_path)
        self.backup_dir = self.save_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.header_data = None  # Store the header document
        
    def load_save_file(self) -> Dict[str, Any]:
        """Load OpenXCom save file preserving order."""
        if not self.save_path.exists():
            raise FileNotFoundError(f"Save file not found: {self.save_path}")
            
        with open(self.save_path, 'r', encoding='utf-8') as f:
            # OpenXCom saves can have multiple YAML documents
            # We want the second document (after the --- separator)
            try:
                documents = list(yaml.load_all(f, Loader=yaml.CLoader))
            except AttributeError:
                f.seek(0)  # Reset file position
                documents = list(yaml.load_all(f, Loader=yaml.Loader))
            
            # Store the header document for later saving
            if len(documents) >= 2:
                self.header_data = documents[0]
                return documents[1]
            elif len(documents) == 1:
                self.header_data = None  # Single document format
                return documents[0]
            else:
                raise ValueError("No valid YAML documents found in save file")
    
    def save_file(self, data: Dict[str, Any]) -> None:
        """Save data to YAML file with proper formatting."""
        with open(self.save_path, 'w', encoding='utf-8') as f:
            # If we have header data, write it first
            if self.header_data is not None:
                yaml.dump(self.header_data, f,
                         default_flow_style=False,
                         allow_unicode=True,
                         width=120,
                         indent=2,
                         sort_keys=False)
                f.write("---\n")  # Document separator
            
            # Write the main game data
            yaml.dump(data, f, 
                     default_flow_style=False,
                     allow_unicode=True,
                     width=120,
                     indent=2,
                     sort_keys=False)
    
    def create_backup(self) -> str:
        """Create a timestamped backup of the current save file."""
        if not self.save_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {self.save_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.save_path.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(self.save_path, backup_path)
        return str(backup_path)
    
    def list_backups(self) -> list[str]:
        """List available backup files sorted by creation time (newest first)."""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_file in self.backup_dir.glob(f"{self.save_path.stem}_*.bak"):
            backups.append(str(backup_file))
        
        # Sort by modification time, newest first
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str) -> None:
        """Restore a backup file to the original save location."""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create a backup of current file before restoring
        if self.save_path.exists():
            restore_backup_name = f"{self.save_path.stem}_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            shutil.copy2(self.save_path, self.backup_dir / restore_backup_name)
        
        shutil.copy2(backup_file, self.save_path)
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the current save file."""
        if not self.save_path.exists():
            return {"exists": False}
        
        stat = self.save_path.stat()
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "path": str(self.save_path),
            "backups_available": len(self.list_backups())
        }


def load_yaml_preserving_order(file_path: str) -> Dict[str, Any]:
    """Load YAML file while preserving key order."""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return yaml.load(f, Loader=yaml.CLoader)
        except AttributeError:
            return yaml.load(f, Loader=yaml.Loader)


def save_yaml_preserving_format(data: Dict[str, Any], file_path: str) -> None:
    """Save YAML data maintaining readable formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f,
                 default_flow_style=False,
                 allow_unicode=True,
                 width=120,
                 indent=2,
                 sort_keys=False)