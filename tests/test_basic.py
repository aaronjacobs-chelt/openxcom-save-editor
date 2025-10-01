"""
Basic tests for the OpenXCom Save Editor.
"""
import pytest
import tempfile
import shutil
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xcom_save_editor import OpenXComSaveEditor
from xcom_save_editor.utils.file_ops import SaveFileManager
from xcom_save_editor.utils.validator import detailed_validate_save


@pytest.fixture
def sample_save_path():
    """Provide path to the sample save file."""
    # Look for SaveGame.sav in the project root
    project_root = Path(__file__).parent.parent
    save_path = project_root / "SaveGame.sav"
    
    if not save_path.exists():
        pytest.skip("SaveGame.sav not found in project root")
    
    return str(save_path)


@pytest.fixture
def temp_save_file(sample_save_path):
    """Create a temporary copy of the save file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as tmp:
        shutil.copy2(sample_save_path, tmp.name)
        yield tmp.name
    
    # Clean up
    Path(tmp.name).unlink(missing_ok=True)


def test_save_file_loading(sample_save_path):
    """Test that we can load the save file."""
    file_manager = SaveFileManager(sample_save_path)
    data = file_manager.load_save_file()
    
    assert isinstance(data, dict)
    assert 'funds' in data
    assert 'bases' in data
    assert isinstance(data['funds'], list)
    assert len(data['funds']) >= 2


def test_editor_creation(sample_save_path):
    """Test that we can create an editor instance."""
    editor = OpenXComSaveEditor(sample_save_path)
    
    assert editor is not None
    assert editor.save_data is not None
    assert editor.original_save_data is not None


def test_editor_status(sample_save_path):
    """Test that we can get status information."""
    editor = OpenXComSaveEditor(sample_save_path)
    status = editor.get_quick_status()
    
    assert isinstance(status, dict)
    assert 'funds' in status
    assert 'research' in status
    assert 'soldiers' in status
    assert 'bases' in status
    
    # Check funds structure
    assert 'current' in status['funds']
    assert 'previous' in status['funds']
    assert isinstance(status['funds']['current'], int)
    assert isinstance(status['funds']['previous'], int)


def test_money_manager(temp_save_file):
    """Test money editing functionality."""
    editor = OpenXComSaveEditor(temp_save_file)
    original_funds = editor.money_manager.get_funds_display()
    
    # Test setting new funds
    new_amount = 5000000
    editor.money_manager.set_current_month_funds(new_amount)
    
    current_funds = editor.money_manager.get_funds_display()
    assert current_funds[0] == new_amount
    assert editor.has_changes() is True
    
    # Test adding funds
    editor.money_manager.add_funds(1000000)
    current_funds = editor.money_manager.get_funds_display()
    assert current_funds[0] == new_amount + 1000000


def test_research_manager(sample_save_path):
    """Test research management functionality."""
    editor = OpenXComSaveEditor(sample_save_path)
    research_manager = editor.research_manager
    
    # Get research projects
    all_projects = research_manager.get_all_research_projects()
    active_projects = research_manager.get_active_research_projects()
    
    assert isinstance(all_projects, list)
    assert isinstance(active_projects, list)
    assert len(active_projects) <= len(all_projects)
    
    # Test research summary
    summary = research_manager.get_research_summary()
    assert isinstance(summary, dict)
    assert 'total_projects' in summary
    assert 'active_projects' in summary


def test_soldier_manager(sample_save_path):
    """Test soldier management functionality."""
    editor = OpenXComSaveEditor(sample_save_path)
    soldier_manager = editor.soldier_manager
    
    # Get soldiers
    all_soldiers = soldier_manager.get_all_soldiers()
    assert isinstance(all_soldiers, list)
    
    if all_soldiers:
        soldier = all_soldiers[0]
        assert hasattr(soldier, 'name')
        assert hasattr(soldier, 'current_stats')
        assert isinstance(soldier.current_stats, dict)


def test_facility_manager(sample_save_path):
    """Test facility management functionality."""
    editor = OpenXComSaveEditor(sample_save_path)
    facility_manager = editor.facility_manager
    
    # Get facilities
    all_facilities = facility_manager.get_all_facilities()
    under_construction = facility_manager.get_facilities_under_construction()
    
    assert isinstance(all_facilities, list)
    assert isinstance(under_construction, list)
    assert len(under_construction) <= len(all_facilities)


def test_production_manager(sample_save_path):
    """Test production management functionality."""
    editor = OpenXComSaveEditor(sample_save_path)
    production_manager = editor.production_manager
    
    # Get production items
    all_items = production_manager.get_all_production_items()
    active_items = production_manager.get_active_production_items()
    
    assert isinstance(all_items, list)
    assert isinstance(active_items, list)
    assert len(active_items) <= len(all_items)


def test_inventory_manager(sample_save_path):
    """Test inventory management functionality."""
    editor = OpenXComSaveEditor(sample_save_path)
    inventory_manager = editor.inventory_manager
    
    # Get inventories
    all_inventories = inventory_manager.get_all_base_inventories()
    assert isinstance(all_inventories, dict)
    
    # Test item search
    all_items = inventory_manager.get_all_unique_items()
    assert isinstance(all_items, list)


def test_backup_creation(temp_save_file):
    """Test backup functionality."""
    editor = OpenXComSaveEditor(temp_save_file)
    
    # Create backup
    backup_path = editor.create_backup()
    assert Path(backup_path).exists()
    
    # Check backup list
    backups = editor.get_available_backups()
    assert len(backups) >= 1
    
    # Cleanup backup
    Path(backup_path).unlink()


def test_validation(sample_save_path):
    """Test save file validation."""
    editor = OpenXComSaveEditor(sample_save_path)
    
    is_valid, errors, warnings = editor.validate_save_data()
    assert is_valid is True
    assert isinstance(errors, list)
    assert isinstance(warnings, list)


def test_changes_tracking(temp_save_file):
    """Test change tracking functionality."""
    editor = OpenXComSaveEditor(temp_save_file)
    
    # Initially no changes
    assert editor.has_changes() is False
    
    # Make a change
    editor.money_manager.set_current_month_funds(9999999)
    assert editor.has_changes() is True
    
    # Get changes summary
    changes = editor.get_all_changes_summary()
    assert isinstance(changes, dict)
    assert 'modified' in changes
    
    # Reset changes
    editor.reset_all_changes()
    assert editor.has_changes() is False


def test_multi_base_support(sample_save_path):
    """Test multi-base functionality."""
    editor = OpenXComSaveEditor(sample_save_path)
    
    # Check that we can handle multiple bases
    base_names = editor.inventory_manager.get_base_names()
    assert isinstance(base_names, list)
    assert len(base_names) >= 1
    
    # Test base-specific operations
    if len(base_names) >= 2:
        # Test inventory for different bases
        base0_inventory = editor.inventory_manager.get_base_inventory(0)
        base1_inventory = editor.inventory_manager.get_base_inventory(1)
        
        assert isinstance(base0_inventory, dict)
        assert isinstance(base1_inventory, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])