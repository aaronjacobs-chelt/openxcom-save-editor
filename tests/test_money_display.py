"""
Tests for MoneyManager funds display and labeling.
"""
import pytest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xcom_save_editor import OpenXComSaveEditor
from xcom_save_editor.game_editors.money_manager import MoneyManager


@pytest.fixture
def sample_save_path():
    """Provide path to the sample save file."""
    project_root = Path(__file__).parent.parent
    save_path = project_root / "SaveGame.sav"
    
    if not save_path.exists():
        pytest.skip("SaveGame.sav not found in project root")
    
    return str(save_path)


def test_funds_display_mapping(sample_save_path):
    """Test that funds display correctly maps current and previous months."""
    editor = OpenXComSaveEditor(sample_save_path)
    money_manager = editor.money_manager
    
    # Get funds display (current, previous)
    current_funds, previous_funds = money_manager.get_funds_display()
    
    # Based on SaveGame.sav content:
    # funds:
    # - 2696270  # previous month (index 0)  
    # - 454802   # current month (index 1)
    assert current_funds == 454802, f"Expected current funds 454802, got {current_funds}"
    assert previous_funds == 2696270, f"Expected previous funds 2696270, got {previous_funds}"


def test_funds_raw_data_structure(sample_save_path):
    """Test that raw funds data structure is as expected."""
    editor = OpenXComSaveEditor(sample_save_path)
    money_manager = editor.money_manager
    
    # Get raw funds array
    funds_list = money_manager.get_funds()
    
    # Should be a list with at least 2 elements
    assert isinstance(funds_list, list), "Funds should be a list"
    assert len(funds_list) >= 2, f"Funds list should have at least 2 elements, got {len(funds_list)}"
    
    # Verify values (funds[0] = previous, funds[1] = current)
    assert funds_list[0] == 2696270, f"funds[0] should be 2696270 (previous), got {funds_list[0]}"
    assert funds_list[1] == 454802, f"funds[1] should be 454802 (current), got {funds_list[1]}"


def test_set_current_month_funds(sample_save_path):
    """Test that setting current month funds works correctly."""
    editor = OpenXComSaveEditor(sample_save_path)
    money_manager = editor.money_manager
    
    # Get original values
    original_current, original_previous = money_manager.get_funds_display()
    
    # Set new current month funds
    new_amount = 5000000
    money_manager.set_current_month_funds(new_amount)
    
    # Verify change
    current_funds, previous_funds = money_manager.get_funds_display()
    assert current_funds == new_amount, f"Current funds should be {new_amount}, got {current_funds}"
    assert previous_funds == original_previous, f"Previous funds should remain {original_previous}, got {previous_funds}"


def test_add_funds_operation(sample_save_path):
    """Test that adding funds works correctly."""
    editor = OpenXComSaveEditor(sample_save_path)
    money_manager = editor.money_manager
    
    # Get original values
    original_current, original_previous = money_manager.get_funds_display()
    
    # Add funds
    add_amount = 1000000
    money_manager.add_funds(add_amount)
    
    # Verify change
    current_funds, previous_funds = money_manager.get_funds_display()
    expected_current = original_current + add_amount
    
    assert current_funds == expected_current, f"Current funds should be {expected_current}, got {current_funds}"
    assert previous_funds == original_previous, f"Previous funds should remain {original_previous}, got {previous_funds}"


def test_funds_display_consistency_with_status(sample_save_path):
    """Test that funds display is consistent between MoneyManager and status display."""
    editor = OpenXComSaveEditor(sample_save_path)
    
    # Get funds from MoneyManager
    money_current, money_previous = editor.money_manager.get_funds_display()
    
    # Get funds from status display
    status = editor.get_quick_status()
    status_current = status['funds']['current']
    status_previous = status['funds']['previous']
    
    # They should match
    assert money_current == status_current, f"MoneyManager current ({money_current}) != Status current ({status_current})"
    assert money_previous == status_previous, f"MoneyManager previous ({money_previous}) != Status previous ({status_previous})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])