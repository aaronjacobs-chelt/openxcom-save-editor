"""
Tests for OpenXCom Save Editor info extraction from header document.
"""
import pytest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xcom_save_editor import OpenXComSaveEditor


@pytest.fixture
def sample_save_path():
    """Provide path to the sample save file."""
    project_root = Path(__file__).parent.parent
    save_path = project_root / "SaveGame.sav"
    
    if not save_path.exists():
        pytest.skip("SaveGame.sav not found in project root")
    
    return str(save_path)


def test_save_info_extracts_from_header(sample_save_path):
    """Test that save info correctly extracts metadata from YAML header document."""
    editor = OpenXComSaveEditor(sample_save_path)
    save_info = editor.get_save_info()
    
    # These values should come from the first YAML document (header)
    assert save_info['save_name'] == 'SaveGame'
    assert save_info['game_version'] == 'Extended 8.3.4'
    assert save_info['game_engine'] == 'Extended'
    
    # These values should come from the second YAML document (game data)
    assert save_info['difficulty'] == 1
    assert save_info['months_passed'] == 1  # Based on SaveGame.sav content
    assert save_info['days_passed'] == 32   # Based on SaveGame.sav content


def test_header_data_preserved(sample_save_path):
    """Test that header data is properly loaded and preserved."""
    editor = OpenXComSaveEditor(sample_save_path)
    
    # Header data should be loaded from first document
    assert editor.file_manager.header_data is not None
    assert isinstance(editor.file_manager.header_data, dict)
    
    # Verify header contains expected keys
    header = editor.file_manager.header_data
    assert 'name' in header
    assert 'version' in header
    assert 'engine' in header
    assert 'mods' in header  # X-Com Files save should have mods list
    
    # Verify specific values
    assert header['name'] == 'SaveGame'
    assert header['version'] == 'Extended 8.3.4'
    assert header['engine'] == 'Extended'


def test_fallback_to_save_data(sample_save_path):
    """Test fallback behavior when header data is missing."""
    editor = OpenXComSaveEditor(sample_save_path)
    
    # Temporarily remove header data to test fallback
    original_header = editor.file_manager.header_data
    editor.file_manager.header_data = None
    
    save_info = editor.get_save_info()
    
    # Should fall back to checking save_data (which won't have these in second document)
    assert save_info['save_name'] == 'Unknown'
    assert save_info['game_version'] == 'Unknown' 
    assert save_info['game_engine'] == 'Unknown'
    
    # But other data should still work
    assert save_info['difficulty'] == 1
    
    # Restore header data
    editor.file_manager.header_data = original_header


if __name__ == "__main__":
    pytest.main([__file__, "-v"])