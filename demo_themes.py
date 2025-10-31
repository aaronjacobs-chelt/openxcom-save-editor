#!/usr/bin/env python3
"""
Demo script to showcase the different UI themes available.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from xcom_save_editor.ui import UIRenderer, set_theme, get_available_themes
from rich.console import Console


def demo_theme(theme_name: str):
    """Demo a specific theme."""
    print(f"\n{'='*60}")
    print(f"Theme: {theme_name.upper()}")
    print(f"{'='*60}")
    
    # Set the theme
    set_theme(theme_name)
    
    # Create renderer
    console = Console()
    renderer = UIRenderer(console)
    
    # Demo welcome screen
    renderer.render_welcome_screen("OpenXCom Save Editor v2.0", "Enhanced UI Demo")
    
    # Demo save info
    sample_save_info = {
        "save_name": "Demo Save",
        "game_version": "Extended 8.3.4",
        "game_engine": "Extended",
        "difficulty": 1,
        "months_passed": 5,
        "days_passed": 127,
        "total_bases": 4,
        "base_names": ["Alpha Base", "Bravo Station", "Charlie Outpost", "Delta Command"],
        "size": 245760,
        "backups_available": 3
    }
    
    renderer.render_save_info(sample_save_info)
    
    # Demo status messages
    renderer.render_success_message("Save loaded successfully")
    renderer.render_info_message("Found 12 research projects")
    renderer.render_warning_message("You have unsaved changes")
    renderer.render_error_message("Failed to create backup")
    
    # Demo status dashboard
    sample_status = {
        "Funds": {"Current": 2500000, "Previous": 1800000},
        "Research": {"Active": 8, "Completed": 45},
        "Facilities": {"Building": 2, "Completed": 28},
        "Production": {"Active": 5, "Total": 15},
        "Bases": {"Total": 4, "Names": ["Alpha", "Bravo", "Charlie", "Delta"]},
        "Soldiers": {"Total": 24, "Deployed": 8}
    }
    
    renderer.render_status_dashboard(sample_status)
    
    # Demo table
    sample_data = [
        {"name": "Plasma Rifle", "quantity": 12, "type": "Weapon"},
        {"name": "Alien Alloys", "quantity": 45, "type": "Material"},
        {"name": "Elerium-115", "quantity": 8, "type": "Material"},
        {"name": "Power Suit", "quantity": 6, "type": "Armor"}
    ]
    
    renderer.render_table_with_data(
        data=sample_data,
        title="🎯 Sample Inventory",
        columns=["name", "quantity", "type"]
    )
    
    # Demo footer with shortcuts
    shortcuts = {
        "s": "Status", "m": "Money", "r": "Research", 
        "q": "Quit", "h": "Help", "t": "Theme"
    }
    
    renderer.render_footer(
        status=f"Theme: {theme_name.title()} | Demo Mode Active",
        shortcuts=shortcuts
    )
    
    print("\n" + "─" * 60 + "\n")


def main():
    """Run the theme demo."""
    print("OpenXCom Save Editor - UI Theme Showcase")
    print("This demo shows all available themes with sample data.")
    
    themes = get_available_themes()
    
    for theme in themes:
        demo_theme(theme)
        if theme != themes[-1]:  # Not the last theme
            input("Press Enter to see next theme...")
    
    print("Theme showcase complete!")
    print(f"You can use any of these themes with: python run_enhanced_editor.py --theme <theme_name>")
    print(f"Available themes: {', '.join(themes)}")


if __name__ == "__main__":
    main()