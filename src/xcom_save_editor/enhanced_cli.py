"""
Enhanced CLI interface with improved theming, navigation, and keyboard shortcuts.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import rich_click as click
from InquirerPy import inquirer
from rich.console import Console

from .editor import OpenXComSaveEditor
from .cli import SaveEditorCLI  # Import original for compatibility
from .ui import UIRenderer, get_current_theme, set_theme, get_available_themes
from .ui.widgets import get_shortcut_manager


class EnhancedSaveEditorCLI:
    """Enhanced CLI with improved theming and navigation."""
    
    def __init__(self):
        self.console = Console()
        self.renderer = UIRenderer(self.console)
        self.shortcut_manager = get_shortcut_manager()
        self.editor: Optional[OpenXComSaveEditor] = None
        self.save_file_path: Optional[str] = None
        
        # Set up keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Configure keyboard shortcuts for the CLI."""
        # These will be integrated with InquirerPy in future updates
        shortcuts = {
            'q': self.handle_exit,
            'h': self.show_help,
            '?': self.show_shortcuts_help,
        }
        
        for key, action in shortcuts.items():
            self.shortcut_manager.register(key, action, f"Action: {action.__name__}")
    
    def _select_with_shortcuts(self, message: str, choices: list, shortcuts: dict = None) -> str:
        """Select prompt with working keyboard shortcuts."""
        
        if not shortcuts:
            return inquirer.select(
                message=message,
                choices=choices,
            ).execute()
        
        while True:
            # Show shortcut prompt first
            try:
                shortcut_keys = ', '.join([f"'{k}'" for k in shortcuts.keys()])
                shortcut_input = inquirer.text(
                    message=f"Enter shortcut ({shortcut_keys}) or press Enter for menu:",
                    default="",
                ).execute().lower().strip()
                
                # Check if it's a valid shortcut
                if shortcut_input in shortcuts:
                    return shortcuts[shortcut_input]
                elif shortcut_input == "":
                    # Show the regular menu
                    return inquirer.select(
                        message="Select an option:",
                        choices=choices,
                    ).execute()
                else:
                    self.renderer.render_warning_message(f"Unknown shortcut: '{shortcut_input}'")
                    continue
                    
            except (KeyboardInterrupt, EOFError):
                return "exit"
    
    def run(self):
        """Main CLI loop with enhanced UI."""
        self.renderer.render_welcome_screen()
        
        # Load save file
        if not self.load_save_file():
            return
        
        # Main menu loop
        while True:
            try:
                # Clear and show current state
                self.renderer.console.print()
                self.renderer.render_changes_status(
                    self.editor.has_changes() if self.editor else False
                )
                
                # Show main menu with shortcuts
                action = self.show_enhanced_main_menu()
                
                if action == "exit":
                    if self.handle_exit():
                        break
                elif action == "status":
                    self.handle_status()
                elif action == "money":
                    self.handle_money_menu()
                elif action == "research":
                    self.handle_research_menu()
                elif action == "soldiers":
                    self.handle_soldiers_menu()
                elif action == "facilities":
                    self.handle_facilities_menu()
                elif action == "production":
                    self.handle_production_menu()
                elif action == "inventory":
                    self.handle_inventory_menu()
                elif action == "backup":
                    self.handle_backup_menu()
                elif action == "save":
                    self.handle_save()
                elif action == "reset":
                    self.handle_reset()
                elif action == "theme":
                    self.handle_theme_menu()
                elif action == "help":
                    self.show_help()
                    
            except KeyboardInterrupt:
                self.renderer.render_warning_message("Operation cancelled")
            except Exception as e:
                self.renderer.render_error_message(f"Error: {e}")
    
    def load_save_file(self) -> bool:
        """Load a save file with enhanced file selection."""
        # Look for .sav files in current directory
        current_dir = Path.cwd()
        save_files = list(current_dir.glob("*.sav"))
        
        if not save_files:
            self.renderer.render_warning_message("No .sav files found in the current directory.")
            file_path = inquirer.filepath(
                message="Enter path to save file:",
                validate=lambda path: Path(path).exists() and Path(path).suffix.lower() == '.sav',
                invalid_message="File must exist and have .sav extension"
            ).execute()
        else:
            # Show available save files with file sizes
            choices = []
            for f in save_files:
                size_mb = f.stat().st_size / 1024 / 1024
                choices.append({
                    "name": f"{f.name} ({size_mb:.1f} MB)",
                    "value": str(f)
                })
            choices.append({"name": "Browse for file...", "value": "browse"})
            
            selected = inquirer.select(
                message="Select save file:",
                choices=choices,
            ).execute()
            
            if selected == "browse":
                file_path = inquirer.filepath(
                    message="Enter path to save file:",
                    validate=lambda path: Path(path).exists() and Path(path).suffix.lower() == '.sav',
                    invalid_message="File must exist and have .sav extension"
                ).execute()
            else:
                file_path = selected
        
        try:
            self.save_file_path = file_path
            self.editor = OpenXComSaveEditor(file_path)
            
            # Show save file info using enhanced renderer
            save_info = self.editor.get_save_info()
            self.renderer.render_save_info(save_info)
            return True
            
        except Exception as e:
            self.renderer.render_error_message(f"Error loading save file: {e}")
            return False
    
    def show_enhanced_main_menu(self) -> str:
        """Show the main menu with enhanced styling and shortcuts."""
        # Show shortcuts help
        shortcuts = {
            "s": "Status", "m": "Money", "r": "Research", "a": "Soldiers", 
            "f": "Facilities", "p": "Production", "i": "Inventory",
            "t": "Theme", "h": "Help", "q": "Quit"
        }
        
        self.renderer.render_footer(
            status="Select an option or use keyboard shortcuts",
            shortcuts=shortcuts
        )
        
        choices = [
            {"name": "[S] 📊 Show Status", "value": "status"},
            {"name": "[M] 💰 Edit Money/Funds", "value": "money"},
            {"name": "[R] 🔬 Manage Research", "value": "research"},
            {"name": "[A] 👤 Edit Soldiers/Agents", "value": "soldiers"},
            {"name": "[F] 🏗️ Manage Facilities", "value": "facilities"},
            {"name": "[P] ⚙️ Manage Production", "value": "production"},
            {"name": "[I] 📦 Edit Inventory", "value": "inventory"},
            {"name": "[B] 🗂️ Backup Management", "value": "backup"},
            {"name": "[T] 🎨 Change Theme", "value": "theme"},
            {"name": "💾 Save Changes", "value": "save"},
            {"name": "↺ Reset All Changes", "value": "reset"},
            {"name": "[H] ❓ Help", "value": "help"},
            {"name": "[Q] ❌ Exit", "value": "exit"},
        ]
        
        return self._select_with_shortcuts(
            message="Select an option:",
            choices=choices,
            shortcuts={
                's': 'status', 'm': 'money', 'r': 'research', 'a': 'soldiers',
                'f': 'facilities', 'p': 'production', 'i': 'inventory', 
                'b': 'backup', 't': 'theme', 'h': 'help', 'q': 'exit'
            }
        )
    
    def handle_status(self):
        """Show enhanced status dashboard."""
        if not self.editor:
            return
        
        self.renderer.push_breadcrumb("Status")
        self.renderer.render_header_with_breadcrumb("Status Dashboard")
        
        status = self.editor.get_quick_status()
        self.renderer.render_status_dashboard(status)
        
        # Wait for user input
        inquirer.confirm("Press Enter to continue...").execute()
        self.renderer.pop_breadcrumb()
    
    def handle_money_menu(self):
        """Handle money editing with enhanced UI."""
        if not self.editor:
            return
        
        self.renderer.push_breadcrumb("Money")
        self.renderer.render_header_with_breadcrumb("Money Management")
        
        current, previous = self.editor.money_manager.get_funds_display()
        
        # Show current funds in a styled way
        funds_info = {
            "Current Funds": self.renderer.format_currency(current),
            "Previous Month": self.renderer.format_currency(previous),
        }
        
        table = self.renderer.layout_manager.create_info_table(
            data=funds_info,
            title="💰 Current Funding Status"
        )
        self.renderer.console.print(table)
        self.renderer.console.print()
        
        choices = [
            {"name": "Set new amount", "value": "set"},
            {"name": "Add funds", "value": "add"},
            {"name": "Back to main menu", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "set":
            amount = inquirer.number(
                message="Enter new amount:",
                min_allowed=0,
                max_allowed=999999999,
                default=current
            ).execute()
            
            self.editor.money_manager.set_current_month_funds(int(amount))
            self.renderer.render_success_message(f"Funds set to {self.renderer.format_currency(int(amount))}")
        
        elif action == "add":
            amount = inquirer.number(
                message="Enter amount to add (negative to subtract):",
                min_allowed=-current,
                max_allowed=999999999,
                default=1000000
            ).execute()
            
            self.editor.money_manager.add_funds(int(amount))
            new_amount = self.editor.money_manager.get_funds_display()[0]
            self.renderer.render_success_message(f"Funds changed to {self.renderer.format_currency(new_amount)}")
        
        self.renderer.pop_breadcrumb()
    
    def handle_research_menu(self):
        """Handle research management with enhanced display."""
        if not self.editor:
            return
        
        self.renderer.push_breadcrumb("Research")
        self.renderer.render_header_with_breadcrumb("Research Management")
        
        research_manager = self.editor.research_manager
        active_projects = research_manager.get_active_research_projects()
        
        if not active_projects:
            self.renderer.render_warning_message("No active research projects found.")
            self.renderer.pop_breadcrumb()
            return
        
        self.renderer.render_info_message(f"Found {len(active_projects)} active research project(s)")
        
        # Show research projects in a table
        project_data = []
        for proj in active_projects:
            project_data.append({
                "name": proj.display_name,
                "progress": f"{proj.progress_percentage:.1f}%"
            })
        
        self.renderer.render_table_with_data(
            data=project_data,
            title="🔬 Active Research Projects",
            columns=["name", "progress"]
        )
        
        choices = [
            {"name": f"Complete all research projects ({len(active_projects)} projects)", "value": "complete_all"},
            {"name": "Complete individual project", "value": "complete_individual"},
            {"name": "Back to main menu", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "complete_all":
            confirm = inquirer.confirm(
                f"Complete all {len(active_projects)} research projects?",
                default=False
            ).execute()
            
            if confirm:
                completed_count = research_manager.complete_all_research_projects()
                self.renderer.render_success_message(f"Completed {completed_count} research projects")
        
        elif action == "complete_individual":
            # Show list of projects
            project_choices = [
                {"name": f"{proj.display_name} ({proj.progress_percentage:.1f}% complete)", "value": proj}
                for proj in active_projects
            ] + [{"name": "Back", "value": "back"}]
            
            selected_project = inquirer.select(
                message="Select project to complete:",
                choices=project_choices,
            ).execute()
            
            if selected_project != "back":
                research_manager.complete_research_project(selected_project)
                self.renderer.render_success_message(f"Completed research: {selected_project.display_name}")
        
        self.renderer.pop_breadcrumb()
    
    def handle_theme_menu(self):
        """Handle theme selection with live preview."""
        self.renderer.push_breadcrumb("Theme")
        self.renderer.render_header_with_breadcrumb("Theme Selection")
        
        current_theme = get_current_theme().theme_name
        available_themes = get_available_themes()
        
        # Show current theme
        self.renderer.render_info_message(f"Current theme: {current_theme.title()}")
        
        # Create theme choices
        theme_choices = [
            {"name": f"{theme.title()} {'(current)' if theme == current_theme else ''}", "value": theme}
            for theme in available_themes
        ] + [{"name": "Back", "value": "back"}]
        
        selected_theme = inquirer.select(
            message="Select theme:",
            choices=theme_choices,
        ).execute()
        
        if selected_theme != "back" and selected_theme != current_theme:
            if self.renderer.set_theme(selected_theme):
                self.renderer.render_success_message(f"Theme changed to {selected_theme.title()}")
                
                # Show a preview of the new theme
                self.renderer.render_info_message("New theme applied!")
                
                # Quick preview
                sample_status = {
                    "Sample": {"Item 1": 100, "Item 2": "Active"},
                    "Preview": {"Colors": "Updated", "Style": "New Theme"}
                }
                self.renderer.render_status_dashboard(sample_status)
            else:
                self.renderer.render_error_message("Failed to change theme")
        
        self.renderer.pop_breadcrumb()
    
    def show_help(self):
        """Show comprehensive help."""
        self.renderer.render_header_with_breadcrumb("Help & Information")
        
        help_text = """
[bold blue]OpenXCom Save Editor v2.0[/bold blue]

This enhanced version includes:
• Multiple theme support (default, dark, light, cyberpunk)
• Improved navigation with breadcrumbs
• Consistent styling and better information display
• Enhanced status dashboard

[bold yellow]Main Features:[/bold yellow]
• Edit funds and resources
• Complete research projects instantly
• Modify soldier stats and abilities
• Manage base facilities and production
• Comprehensive backup system

[bold green]Keyboard Shortcuts:[/bold green]
• s - Status dashboard
• m - Money management
• r - Research management
• a - Soldier (agents) management
• f - Facilities management
• p - Production management
• i - Inventory management
• t - Theme selection
• h - This help screen
• q - Quit application

[bold red]Important Notes:[/bold red]
• Always backup your saves before editing
• This editor is designed for OpenXCom Extended + X-Com Files mod
• Changes are not saved until you explicitly save them
        """
        
        self.renderer.console.print(help_text)
        inquirer.confirm("Press Enter to continue...").execute()
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help."""
        shortcuts = self.shortcut_manager.get_shortcut_help("menu")
        self.renderer.render_footer(shortcuts=shortcuts)
        inquirer.confirm("Press Enter to continue...").execute()
    
    def handle_soldiers_menu(self):
        """Placeholder - delegate to original CLI for now."""
        # For now, we'll use the original implementation
        original_cli = SaveEditorCLI()
        original_cli.editor = self.editor
        original_cli.handle_soldiers_menu()
    
    def handle_facilities_menu(self):
        """Placeholder - delegate to original CLI for now."""
        original_cli = SaveEditorCLI()
        original_cli.editor = self.editor
        original_cli.handle_facilities_menu()
    
    def handle_production_menu(self):
        """Placeholder - delegate to original CLI for now."""
        original_cli = SaveEditorCLI()
        original_cli.editor = self.editor
        original_cli.handle_production_menu()
    
    def handle_inventory_menu(self):
        """Placeholder - delegate to original CLI for now."""
        original_cli = SaveEditorCLI()
        original_cli.editor = self.editor
        original_cli.handle_inventory_menu()
    
    def handle_backup_menu(self):
        """Placeholder - delegate to original CLI for now."""
        original_cli = SaveEditorCLI()
        original_cli.editor = self.editor
        original_cli.handle_backup_menu()
    
    def handle_save(self):
        """Handle saving with enhanced feedback."""
        if not self.editor:
            return
        
        if not self.editor.has_changes():
            self.renderer.render_warning_message("No changes to save.")
            return
        
        # Show changes summary
        changes = self.editor.get_all_changes_summary()
        
        if changes['modified']:
            self.renderer.render_info_message("Changes to be saved:")
            for key, change in changes['modified'].items():
                field = change.get('field', key)
                current = change.get('current', 'Modified')
                self.renderer.console.print(f"  • {field}: {current}")
            self.renderer.console.print()
        
        # Confirm save
        confirm = inquirer.confirm(
            "Save these changes to the file?",
            default=True
        ).execute()
        
        if confirm:
            create_backup = inquirer.confirm(
                "Create backup before saving?",
                default=True
            ).execute()
            
            success = self.editor.commit_changes(create_backup)
            if success:
                self.renderer.render_success_message("Changes saved successfully!")
                if create_backup:
                    self.renderer.render_success_message("Backup created before saving")
            else:
                self.renderer.render_error_message("Failed to save changes")
    
    def handle_reset(self):
        """Handle resetting changes with enhanced feedback."""
        if not self.editor:
            return
        
        if not self.editor.has_changes():
            self.renderer.render_warning_message("No changes to reset.")
            return
        
        # Show what will be reset
        changes = self.editor.get_all_changes_summary()
        
        if changes['modified']:
            self.renderer.render_info_message("Changes that will be reset:")
            for key, change in changes['modified'].items():
                field = change.get('field', key)
                current = change.get('current', 'Modified')
                self.renderer.console.print(f"  • {field}: {current}")
            self.renderer.console.print()
        
        confirm = inquirer.confirm(
            "Reset all changes to original values?",
            default=False
        ).execute()
        
        if confirm:
            self.editor.reset_all_changes()
            self.renderer.render_success_message("All changes reset to original values")
    
    def handle_exit(self) -> bool:
        """Handle exit with enhanced unsaved changes check."""
        if not self.editor:
            return True
        
        if self.editor.has_changes():
            self.renderer.render_warning_message("You have unsaved changes!")
            
            action = inquirer.select(
                message="What would you like to do?",
                choices=[
                    {"name": "Save changes and exit", "value": "save"},
                    {"name": "Exit without saving", "value": "discard"},
                    {"name": "Cancel (don't exit)", "value": "cancel"},
                ],
            ).execute()
            
            if action == "save":
                if self._save_on_exit():
                    self.renderer.render_success_message("Goodbye!")
                    return True
                else:
                    return False
            elif action == "discard":
                confirm = inquirer.confirm(
                    "Are you sure you want to exit without saving?",
                    default=False
                ).execute()
                
                if confirm:
                    self.renderer.render_warning_message("Changes discarded. Goodbye!")
                    return True
                else:
                    return False
            else:  # cancel
                return False
        else:
            self.renderer.render_success_message("Goodbye!")
            return True
    
    def _save_on_exit(self) -> bool:
        """Save when exiting."""
        create_backup = inquirer.confirm(
            "Create backup before saving?",
            default=True
        ).execute()
        
        success = self.editor.commit_changes(create_backup)
        if success:
            self.renderer.render_success_message("Changes saved successfully!")
            if create_backup:
                self.renderer.render_success_message("Backup created before saving")
        else:
            self.renderer.render_error_message("Failed to save changes")
        
        return success


@click.command()
@click.option('--theme', type=click.Choice(['default', 'dark', 'light', 'cyberpunk']), 
              help='Set the UI theme')
@click.option('--legacy', is_flag=True, help='Use the original CLI interface')
def main(theme, legacy):
    """Enhanced OpenXCom Save Editor with improved UI and theming."""
    
    # Set theme if specified
    if theme:
        set_theme(theme)
    
    try:
        if legacy:
            # Use original CLI
            cli = SaveEditorCLI()
            cli.run()
        else:
            # Use enhanced CLI
            cli = EnhancedSaveEditorCLI()
            cli.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()