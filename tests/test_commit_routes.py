"""
Tests for save/commit functionality to ensure both CLI routes work consistently.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xcom_save_editor import OpenXComSaveEditor
from xcom_save_editor.cli import SaveEditorCLI


@pytest.fixture
def sample_save_path():
    """Provide path to the sample save file."""
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


def test_direct_commit_changes(temp_save_file):
    """Test that direct editor.commit_changes() works and persists changes."""
    # Load editor and make a change
    editor = OpenXComSaveEditor(temp_save_file)
    
    # Initially no changes
    assert editor.has_changes() is False
    
    # Make a change to funds
    original_funds = editor.money_manager.get_funds_display()
    new_amount = original_funds[0] + 100000
    editor.money_manager.set_current_month_funds(new_amount)
    
    # Should now have changes
    assert editor.has_changes() is True
    
    # Commit changes
    success = editor.commit_changes(create_backup=False)  # Skip backup for test
    assert success is True
    
    # Should no longer have changes after commit
    assert editor.has_changes() is False
    
    # Reload the file and verify persistence
    editor2 = OpenXComSaveEditor(temp_save_file)
    reloaded_funds = editor2.money_manager.get_funds_display()
    assert reloaded_funds[0] == new_amount, f"Expected {new_amount}, got {reloaded_funds[0]}"


def test_cli_handle_save_method(temp_save_file):
    """Test that CLI handle_save method works correctly."""
    # Create CLI instance and load editor
    cli = SaveEditorCLI()
    cli.editor = OpenXComSaveEditor(temp_save_file)
    
    # Make a change
    original_funds = cli.editor.money_manager.get_funds_display()
    new_amount = original_funds[0] + 200000
    cli.editor.money_manager.set_current_month_funds(new_amount)
    
    # Should have changes
    assert cli.editor.has_changes() is True
    
    # Mock user inputs for CLI interaction
    with patch('xcom_save_editor.cli.inquirer') as mock_inquirer:
        # Mock confirmation dialogs to always return True
        mock_inquirer.confirm.return_value.execute.return_value = True
        
        # Call handle_save method
        cli.handle_save()
    
    # Should no longer have changes after save
    assert cli.editor.has_changes() is False
    
    # Reload and verify persistence
    editor2 = OpenXComSaveEditor(temp_save_file)
    reloaded_funds = editor2.money_manager.get_funds_display()
    assert reloaded_funds[0] == new_amount, f"Expected {new_amount}, got {reloaded_funds[0]}"


def test_cli_save_on_exit_method(temp_save_file):
    """Test that CLI handle_save_on_exit method works correctly."""
    # Create CLI instance and load editor
    cli = SaveEditorCLI()
    cli.editor = OpenXComSaveEditor(temp_save_file)
    
    # Make a change
    original_funds = cli.editor.money_manager.get_funds_display()
    new_amount = original_funds[0] + 300000
    cli.editor.money_manager.set_current_month_funds(new_amount)
    
    # Should have changes
    assert cli.editor.has_changes() is True
    
    # Mock user input for backup confirmation
    with patch('xcom_save_editor.cli.inquirer') as mock_inquirer:
        # Mock backup confirmation to return True
        mock_inquirer.confirm.return_value.execute.return_value = True
        
        # Call handle_save_on_exit method
        success = cli.handle_save_on_exit()
    
    # Should succeed and reset changes
    assert success is True
    assert cli.editor.has_changes() is False
    
    # Reload and verify persistence
    editor2 = OpenXComSaveEditor(temp_save_file)
    reloaded_funds = editor2.money_manager.get_funds_display()
    assert reloaded_funds[0] == new_amount, f"Expected {new_amount}, got {reloaded_funds[0]}"


def test_save_methods_consistency(temp_save_file):
    """Test that both CLI save methods produce identical results."""
    # Test regular save
    cli1 = SaveEditorCLI()
    cli1.editor = OpenXComSaveEditor(temp_save_file)
    
    # Make change and save via handle_save
    original_funds = cli1.editor.money_manager.get_funds_display()
    test_amount1 = original_funds[0] + 100
    cli1.editor.money_manager.set_current_month_funds(test_amount1)
    
    with patch('xcom_save_editor.cli.inquirer') as mock_inquirer:
        mock_inquirer.confirm.return_value.execute.return_value = True
        cli1.handle_save()
    
    assert cli1.editor.has_changes() is False
    
    # Make another change and save via handle_save_on_exit
    test_amount2 = test_amount1 + 100
    cli1.editor.money_manager.set_current_month_funds(test_amount2)
    
    with patch('xcom_save_editor.cli.inquirer') as mock_inquirer:
        mock_inquirer.confirm.return_value.execute.return_value = True
        success = cli1.handle_save_on_exit()
    
    assert success is True
    assert cli1.editor.has_changes() is False
    
    # Verify final result
    editor_final = OpenXComSaveEditor(temp_save_file)
    final_funds = editor_final.money_manager.get_funds_display()
    assert final_funds[0] == test_amount2


def test_changes_tracking_after_commit(temp_save_file):
    """Test that has_changes() correctly resets after commit_changes()."""
    editor = OpenXComSaveEditor(temp_save_file)
    
    # Initially no changes
    assert editor.has_changes() is False
    
    # Make multiple changes
    editor.money_manager.set_current_month_funds(9999999)
    assert editor.has_changes() is True
    
    # Commit changes
    success = editor.commit_changes(create_backup=False)
    assert success is True
    
    # Changes should be reset
    assert editor.has_changes() is False
    
    # Original data should be updated to current state
    # Make another change to verify tracking still works
    editor.money_manager.add_funds(1000)
    assert editor.has_changes() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])