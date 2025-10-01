"""
Interactive CLI interface for the OpenXCom save editor.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from .editor import OpenXComSaveEditor


class SaveEditorCLI:
    """Interactive CLI for the OpenXCom save editor."""
    
    def __init__(self):
        self.console = Console()
        self.editor: Optional[OpenXComSaveEditor] = None
        self.save_file_path: Optional[str] = None
    
    def run(self):
        """Main CLI loop."""
        self.show_welcome()
        
        # Load save file
        if not self.load_save_file():
            return
        
        # Main menu loop
        while True:
            try:
                action = self.show_main_menu()
                
                if action == "exit":
                    if self.handle_exit():
                        break
                elif action == "status":
                    self.show_status()
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
                    
            except KeyboardInterrupt:
                rprint("\n[yellow]Operation cancelled[/yellow]")
            except Exception as e:
                rprint(f"[red]Error: {e}[/red]")
    
    def show_welcome(self):
        """Show welcome message."""
        welcome_text = Text("OpenXCom Save Editor", style="bold blue")
        welcome_panel = Panel(
            welcome_text,
            subtitle="Edit your X-Com Files saves safely",
            border_style="blue"
        )
        self.console.print()
        self.console.print(welcome_panel)
        self.console.print()
    
    def load_save_file(self) -> bool:
        """Load a save file."""
        # Look for .sav files in current directory
        current_dir = Path.cwd()
        save_files = list(current_dir.glob("*.sav"))
        
        if not save_files:
            rprint("[red]No .sav files found in the current directory.[/red]")
            file_path = inquirer.filepath(
                message="Enter path to save file:",
                validate=lambda path: Path(path).exists() and Path(path).suffix.lower() == '.sav',
                invalid_message="File must exist and have .sav extension"
            ).execute()
        else:
            # Show available save files
            choices = [str(f) for f in save_files] + ["Browse for file..."]
            
            selected = inquirer.select(
                message="Select save file:",
                choices=choices,
            ).execute()
            
            if selected == "Browse for file...":
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
            
            # Show save file info
            self.show_save_info()
            return True
            
        except Exception as e:
            rprint(f"[red]Error loading save file: {e}[/red]")
            return False
    
    def show_save_info(self):
        """Show information about the loaded save file."""
        if not self.editor:
            return
            
        info = self.editor.get_save_info()
        
        table = Table(title="Save Game Information", border_style="green")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Save Name", info['save_name'])
        table.add_row("Game Version", info['game_version'])
        table.add_row("Engine", info['game_engine'])
        table.add_row("Difficulty", str(info['difficulty']))
        table.add_row("Months Passed", str(info['months_passed']))
        table.add_row("Days Passed", str(info['days_passed']))
        table.add_row("Total Bases", str(info['total_bases']))
        
        if info['base_names']:
            table.add_row("Bases", ", ".join(info['base_names']))
        
        table.add_row("File Size", f"{info['size']:,} bytes")
        table.add_row("Backups Available", str(info['backups_available']))
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def show_main_menu(self) -> str:
        """Show the main menu and return selected action."""
        # Show changes indicator
        if self.editor and self.editor.has_changes():
            changes_text = "[yellow]⚠ You have unsaved changes[/yellow]"
        else:
            changes_text = "[green]✓ No unsaved changes[/green]"
        
        self.console.print(changes_text)
        self.console.print()
        
        choices = [
            {"name": "📊 Show Status", "value": "status"},
            {"name": "💰 Edit Money/Funds", "value": "money"},
            {"name": "🔬 Manage Research", "value": "research"},
            {"name": "👤 Edit Soldiers/Agents", "value": "soldiers"},
            {"name": "🏗️ Manage Facilities", "value": "facilities"},
            {"name": "⚙️ Manage Production", "value": "production"},
            {"name": "📦 Edit Inventory", "value": "inventory"},
            {"name": "🗂️ Backup Management", "value": "backup"},
            {"name": "💾 Save Changes", "value": "save"},
            {"name": "↺ Reset All Changes", "value": "reset"},
            {"name": "❌ Exit", "value": "exit"},
        ]
        
        return inquirer.select(
            message="Select an option:",
            choices=choices,
        ).execute()
    
    def show_status(self):
        """Show current game status."""
        if not self.editor:
            return
        
        status = self.editor.get_quick_status()
        
        # Money panel
        money_text = f"Current: ${status['funds']['current']:,}\nPrevious: ${status['funds']['previous']:,}"
        money_panel = Panel(money_text, title="💰 Funds", border_style="green")
        
        # Research panel
        research_text = f"Active: {status['research']['active']}\nCompleted: {status['research']['completed']}"
        research_panel = Panel(research_text, title="🔬 Research", border_style="blue")
        
        # Facilities panel
        facilities_text = f"Building: {status['facilities']['building']}\nCompleted: {status['facilities']['completed']}"
        facilities_panel = Panel(facilities_text, title="🏗️ Facilities", border_style="yellow")
        
        # Production panel
        production_text = f"Active: {status['production']['active']}\nTotal: {status['production']['total']}"
        production_panel = Panel(production_text, title="⚙️ Production", border_style="magenta")
        
        # Bases panel
        bases_text = f"Total Bases: {status['bases']['total']}\n" + "\n".join(status['bases']['names'])
        bases_panel = Panel(bases_text, title="🏠 Bases", border_style="cyan")
        
        # Soldiers panel
        soldiers_text = f"Total Soldiers: {status['soldiers']['total']}"
        soldiers_panel = Panel(soldiers_text, title="👤 Soldiers", border_style="red")
        
        self.console.print()
        
        # Print panels in a grid-like fashion
        from rich.columns import Columns
        self.console.print(Columns([money_panel, research_panel]))
        self.console.print(Columns([facilities_panel, production_panel]))
        self.console.print(Columns([bases_panel, soldiers_panel]))
        
        self.console.print()
        
        # Wait for user input
        inquirer.confirm("Press Enter to continue...").execute()
    
    def handle_money_menu(self):
        """Handle money editing menu."""
        if not self.editor:
            return
        
        current, previous = self.editor.money_manager.get_funds_display()
        
        rprint(f"[green]Current Funds: ${current:,}[/green]")
        rprint(f"[blue]Previous Month: ${previous:,}[/blue]")
        rprint()
        
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
            rprint(f"[green]✓ Funds set to ${int(amount):,}[/green]")
        
        elif action == "add":
            amount = inquirer.number(
                message="Enter amount to add (negative to subtract):",
                min_allowed=-current,
                max_allowed=999999999,
                default=1000000
            ).execute()
            
            self.editor.money_manager.add_funds(int(amount))
            new_amount = self.editor.money_manager.get_funds_display()[0]
            rprint(f"[green]✓ Funds changed to ${new_amount:,}[/green]")
    
    def handle_research_menu(self):
        """Handle research management menu."""
        if not self.editor:
            return
        
        research_manager = self.editor.research_manager
        active_projects = research_manager.get_active_research_projects()
        
        if not active_projects:
            rprint("[yellow]No active research projects found.[/yellow]")
            return
        
        rprint(f"[blue]Found {len(active_projects)} active research project(s)[/blue]")
        rprint()
        
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
                rprint(f"[green]✓ Completed {completed_count} research projects[/green]")
        
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
                rprint(f"[green]✓ Completed research: {selected_project.display_name}[/green]")
    
    def handle_soldiers_menu(self):
        """Handle soldier/agent editing menu."""
        if not self.editor:
            return
        
        soldier_manager = self.editor.soldier_manager
        soldiers = soldier_manager.get_all_soldiers()
        
        if not soldiers:
            rprint("[yellow]No soldiers found.[/yellow]")
            return
        
        rprint(f"[blue]Found {len(soldiers)} soldier(s)[/blue]")
        rprint()
        
        choices = [
            {"name": f"Set all soldiers to max stats ({len(soldiers)} soldiers)", "value": "max_all"},
            {"name": "Set custom max value for all soldiers", "value": "custom_all"},
            {"name": "Edit individual soldier", "value": "individual"},
            {"name": "Back to main menu", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "max_all":
            confirm = inquirer.confirm(
                f"Set all {len(soldiers)} soldiers to maximum stats (100)?",
                default=False
            ).execute()
            
            if confirm:
                modified_count = soldier_manager.set_all_soldiers_stats_to_max(100)
                rprint(f"[green]✓ Set {modified_count} soldiers to max stats[/green]")
        
        elif action == "custom_all":
            max_value = inquirer.number(
                message="Enter maximum stat value (1-255):",
                min_allowed=1,
                max_allowed=255,
                default=100
            ).execute()
            
            confirm = inquirer.confirm(
                f"Set all {len(soldiers)} soldiers to stat value {int(max_value)}?",
                default=False
            ).execute()
            
            if confirm:
                modified_count = soldier_manager.set_all_soldiers_stats_to_max(int(max_value))
                rprint(f"[green]✓ Set {modified_count} soldiers to stat value {int(max_value)}[/green]")
        
        elif action == "individual":
            # Show list of soldiers
            soldier_choices = [
                {"name": f"{soldier.name} - Rank {soldier.rank} - {soldier.missions} missions", "value": soldier}
                for soldier in soldiers
            ] + [{"name": "Back", "value": "back"}]
            
            selected_soldier = inquirer.select(
                message="Select soldier to edit:",
                choices=soldier_choices,
            ).execute()
            
            if selected_soldier != "back":
                self.handle_individual_soldier_edit(selected_soldier)
    
    def handle_individual_soldier_edit(self, soldier):
        """Handle editing individual soldier stats."""
        soldier_manager = self.editor.soldier_manager
        
        # Show current stats
        rprint(f"[blue]Editing: {soldier.name}[/blue]")
        rprint()
        
        table = Table(title=f"{soldier.name}'s Current Stats")
        table.add_column("Stat", style="cyan")
        table.add_column("Value", style="white")
        
        from .game_editors.soldier_manager import Soldier
        for stat_name in Soldier.STATS:
            current_value = soldier.get_stat(stat_name)
            formatted_stat = stat_name.replace('psi', 'Psi ').replace('Strength', ' Strength').replace('Skill', ' Skill')
            table.add_row(formatted_stat.title(), str(current_value))
        
        self.console.print(table)
        rprint()
        
        choices = [
            {"name": "Set all stats to maximum (100)", "value": "max"},
            {"name": "Set all stats to custom value", "value": "custom"},
            {"name": "Edit individual stat", "value": "individual_stat"},
            {"name": "Back", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "max":
            soldier_manager.set_soldier_stats_to_max(soldier, 100)
            rprint(f"[green]✓ Set all stats to 100 for {soldier.name}[/green]")
        
        elif action == "custom":
            value = inquirer.number(
                message="Enter stat value (1-255):",
                min_allowed=1,
                max_allowed=255,
                default=100
            ).execute()
            
            soldier_manager.set_soldier_stats_to_max(soldier, int(value))
            rprint(f"[green]✓ Set all stats to {int(value)} for {soldier.name}[/green]")
        
        elif action == "individual_stat":
            from .game_editors.soldier_manager import Soldier
            stat_choices = [{"name": name.title(), "value": name} for name in Soldier.STATS] + [{"name": "Back", "value": "back"}]
            
            selected_stat = inquirer.select(
                message="Select stat to edit:",
                choices=stat_choices,
            ).execute()
            
            if selected_stat != "back":
                current_value = soldier.get_stat(selected_stat)
                new_value = inquirer.number(
                    message=f"Enter new value for {selected_stat} (current: {current_value}):",
                    min_allowed=0,
                    max_allowed=255,
                    default=current_value
                ).execute()
                
                soldier_manager.set_soldier_stat(soldier, selected_stat, int(new_value))
                rprint(f"[green]✓ Set {selected_stat} to {int(new_value)} for {soldier.name}[/green]")
    
    def handle_facilities_menu(self):
        """Handle facility management menu."""
        if not self.editor:
            return
        
        facility_manager = self.editor.facility_manager
        under_construction = facility_manager.get_facilities_under_construction()
        
        if not under_construction:
            rprint("[yellow]No facilities under construction.[/yellow]")
            return
        
        rprint(f"[blue]Found {len(under_construction)} facility(s) under construction[/blue]")
        rprint()
        
        # Show facilities under construction
        table = Table(title="Facilities Under Construction")
        table.add_column("Base", style="cyan")
        table.add_column("Facility", style="white")
        table.add_column("Time Remaining", style="yellow")
        
        base_names = facility_manager.get_base_names()
        for facility in under_construction:
            base_name = base_names[facility.base_index] if facility.base_index < len(base_names) else f"Base {facility.base_index + 1}"
            table.add_row(base_name, facility.display_name, f"{facility.build_time_remaining} hours")
        
        self.console.print(table)
        rprint()
        
        choices = [
            {"name": f"Complete all facility construction ({len(under_construction)} facilities)", "value": "complete_all"},
            {"name": "Complete individual facility", "value": "complete_individual"},
            {"name": "Back to main menu", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "complete_all":
            confirm = inquirer.confirm(
                f"Complete construction of all {len(under_construction)} facilities?",
                default=False
            ).execute()
            
            if confirm:
                completed_count = facility_manager.complete_all_facility_construction()
                rprint(f"[green]✓ Completed construction of {completed_count} facilities[/green]")
        
        elif action == "complete_individual":
            base_names = facility_manager.get_base_names()
            facility_choices = [
                {"name": f"{base_names[f.base_index]}: {f.display_name} ({f.build_time_remaining}h)", "value": f}
                for f in under_construction
            ] + [{"name": "Back", "value": "back"}]
            
            selected_facility = inquirer.select(
                message="Select facility to complete:",
                choices=facility_choices,
            ).execute()
            
            if selected_facility != "back":
                facility_manager.complete_facility_construction(selected_facility)
                rprint(f"[green]✓ Completed construction: {selected_facility.display_name}[/green]")
    
    def handle_production_menu(self):
        """Handle production management menu."""
        if not self.editor:
            return
        
        production_manager = self.editor.production_manager
        active_items = production_manager.get_active_production_items()
        
        if not active_items:
            rprint("[yellow]No active production items.[/yellow]")
            return
        
        rprint(f"[blue]Found {len(active_items)} active production item(s)[/blue]")
        rprint()
        
        choices = [
            {"name": f"Complete all production items ({len(active_items)} items)", "value": "complete_all"},
            {"name": "Complete individual item", "value": "complete_individual"},
            {"name": "Back to main menu", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "complete_all":
            confirm = inquirer.confirm(
                f"Complete production of all {len(active_items)} items?",
                default=False
            ).execute()
            
            if confirm:
                completed_count = production_manager.complete_all_production_items()
                rprint(f"[green]✓ Completed production of {completed_count} items[/green]")
        
        elif action == "complete_individual":
            base_names = production_manager.get_base_names()
            item_choices = [
                {"name": f"{base_names[item.base_index]}: {item.display_name} x{item.amount_to_produce} ({item.time_spent}h)", "value": item}
                for item in active_items
            ] + [{"name": "Back", "value": "back"}]
            
            selected_item = inquirer.select(
                message="Select item to complete:",
                choices=item_choices,
            ).execute()
            
            if selected_item != "back":
                production_manager.complete_production_item(selected_item)
                rprint(f"[green]✓ Completed production: {selected_item.display_name}[/green]")
    
    def handle_inventory_menu(self):
        """Handle inventory management menu."""
        if not self.editor:
            return
        
        inventory_manager = self.editor.inventory_manager
        base_names = inventory_manager.get_base_names()
        
        if not base_names:
            rprint("[yellow]No bases found.[/yellow]")
            return
        
        # Select base
        base_choices = [
            {"name": f"{i+1}. {name}", "value": i}
            for i, name in enumerate(base_names)
        ] + [{"name": "Back to main menu", "value": "back"}]
        
        selected_base = inquirer.select(
            message="Select base to manage inventory:",
            choices=base_choices,
        ).execute()
        
        if selected_base == "back":
            return
        
        inventory = inventory_manager.get_base_inventory(selected_base)
        
        if not inventory:
            rprint(f"[yellow]No items in {base_names[selected_base]}.[/yellow]")
            return
        
        # Show current inventory
        rprint(f"[blue]{base_names[selected_base]} Inventory ({len(inventory)} item types):[/blue]")
        rprint()
        
        table = Table(title=f"{base_names[selected_base]} Inventory")
        table.add_column("Item", style="cyan")
        table.add_column("Quantity", style="white")
        
        # Sort by quantity (descending)
        sorted_items = sorted(inventory.items(), key=lambda x: x[1], reverse=True)
        
        for item_name, quantity in sorted_items[:20]:  # Show top 20 items
            display_name = inventory_manager._format_item_name(item_name)
            table.add_row(display_name, f"{quantity:,}")
        
        if len(sorted_items) > 20:
            table.add_row("...", f"... and {len(sorted_items) - 20} more items")
        
        self.console.print(table)
        rprint()
        
        choices = [
            {"name": "Edit item quantity", "value": "edit_quantity"},
            {"name": "Search for item", "value": "search"},
            {"name": "Back", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "edit_quantity":
            # Select item to edit
            item_choices = [
                {"name": f"{inventory_manager._format_item_name(name)} ({qty:,})", "value": name}
                for name, qty in sorted_items
            ] + [{"name": "Back", "value": "back"}]
            
            selected_item = inquirer.select(
                message="Select item to edit:",
                choices=item_choices,
                height=15
            ).execute()
            
            if selected_item != "back":
                current_qty = inventory[selected_item]
                new_qty = inquirer.number(
                    message=f"Enter new quantity (current: {current_qty:,}):",
                    min_allowed=0,
                    max_allowed=9999999,
                    default=current_qty
                ).execute()
                
                inventory_manager.set_item_quantity(selected_base, selected_item, int(new_qty))
                display_name = inventory_manager._format_item_name(selected_item)
                rprint(f"[green]✓ Set {display_name} to {int(new_qty):,}[/green]")
        
        elif action == "search":
            search_term = inquirer.text(
                message="Enter search term:",
                validate=lambda x: len(x) >= 2,
                invalid_message="Search term must be at least 2 characters"
            ).execute()
            
            matching_items = inventory_manager.search_items(search_term)
            
            if matching_items:
                rprint(f"[green]Found {len(matching_items)} matching item(s):[/green]")
                
                for item_name, total_qty in matching_items.items():
                    display_name = inventory_manager._format_item_name(item_name)
                    base_qty = inventory_manager.get_item_quantity(selected_base, item_name)
                    rprint(f"  {display_name}: {base_qty:,} (total across all bases: {total_qty:,})")
            else:
                rprint(f"[yellow]No items found matching '{search_term}'[/yellow]")
    
    def handle_backup_menu(self):
        """Handle backup management menu."""
        if not self.editor:
            return
        
        backups = self.editor.get_available_backups()
        
        if not backups:
            rprint("[yellow]No backups available.[/yellow]")
            
            create_backup = inquirer.confirm(
                "Would you like to create a backup now?",
                default=True
            ).execute()
            
            if create_backup:
                backup_path = self.editor.create_backup()
                rprint(f"[green]✓ Backup created: {Path(backup_path).name}[/green]")
            
            return
        
        # Show available backups
        table = Table(title="Available Backups")
        table.add_column("Backup Name", style="cyan")
        table.add_column("Size", style="white")
        table.add_column("Created", style="yellow")
        
        for backup in backups:
            size_mb = backup['size'] / 1024 / 1024
            created_time = datetime.fromtimestamp(backup['created'])
            table.add_row(
                backup['name'], 
                f"{size_mb:.2f} MB",
                created_time.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        self.console.print(table)
        rprint()
        
        choices = [
            {"name": "Create new backup", "value": "create"},
            {"name": "Restore from backup", "value": "restore"},
            {"name": "Back to main menu", "value": "back"},
        ]
        
        action = inquirer.select(
            message="What would you like to do?",
            choices=choices,
        ).execute()
        
        if action == "create":
            backup_path = self.editor.create_backup()
            rprint(f"[green]✓ Backup created: {Path(backup_path).name}[/green]")
        
        elif action == "restore":
            backup_choices = [
                {"name": f"{backup['name']} ({datetime.fromtimestamp(backup['created']).strftime('%Y-%m-%d %H:%M:%S')})", "value": backup['path']}
                for backup in backups
            ] + [{"name": "Back", "value": "back"}]
            
            selected_backup = inquirer.select(
                message="Select backup to restore:",
                choices=backup_choices,
            ).execute()
            
            if selected_backup != "back":
                confirm = inquirer.confirm(
                    "This will overwrite your current save file. Continue?",
                    default=False
                ).execute()
                
                if confirm:
                    if self.editor.restore_backup(selected_backup):
                        rprint("[green]✓ Backup restored successfully[/green]")
                    else:
                        rprint("[red]✗ Failed to restore backup[/red]")
    
    def handle_save(self):
        """Handle saving changes."""
        if not self.editor:
            return
        
        if not self.editor.has_changes():
            rprint("[yellow]No changes to save.[/yellow]")
            return
        
        # Show changes summary
        changes = self.editor.get_all_changes_summary()
        
        if changes['modified']:
            rprint("[blue]Changes to be saved:[/blue]")
            for key, change in changes['modified'].items():
                rprint(f"  • {change.get('field', key)}: {change.get('current', 'Modified')}")
            rprint()
        
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
            
            if self.editor.commit_changes(create_backup):
                rprint("[green]✓ Changes saved successfully![/green]")
                if create_backup:
                    rprint("[green]✓ Backup created before saving[/green]")
            else:
                rprint("[red]✗ Failed to save changes[/red]")
    
    def handle_reset(self):
        """Handle resetting all changes."""
        if not self.editor:
            return
        
        if not self.editor.has_changes():
            rprint("[yellow]No changes to reset.[/yellow]")
            return
        
        # Show what will be reset
        changes = self.editor.get_all_changes_summary()
        
        if changes['modified']:
            rprint("[blue]Changes that will be reset:[/blue]")
            for key, change in changes['modified'].items():
                rprint(f"  • {change.get('field', key)}: {change.get('current', 'Modified')}")
            rprint()
        
        confirm = inquirer.confirm(
            "Reset all changes to original values?",
            default=False
        ).execute()
        
        if confirm:
            self.editor.reset_all_changes()
            rprint("[green]✓ All changes reset to original values[/green]")
    
    def handle_exit(self) -> bool:
        """Handle exit with unsaved changes check."""
        if not self.editor:
            return True
        
        if self.editor.has_changes():
            rprint("[yellow]You have unsaved changes![/yellow]")
            
            action = inquirer.select(
                message="What would you like to do?",
                choices=[
                    {"name": "Save changes and exit", "value": "save"},
                    {"name": "Exit without saving", "value": "discard"},
                    {"name": "Cancel (don't exit)", "value": "cancel"},
                ],
            ).execute()
            
            if action == "save":
                if self.handle_save_on_exit():
                    rprint("[green]Goodbye![/green]")
                    return True
                else:
                    return False
            elif action == "discard":
                confirm = inquirer.confirm(
                    "Are you sure you want to exit without saving?",
                    default=False
                ).execute()
                
                if confirm:
                    rprint("[yellow]Changes discarded. Goodbye![/yellow]")
                    return True
                else:
                    return False
            else:  # cancel
                return False
        else:
            rprint("[green]Goodbye![/green]")
            return True
    
    def handle_save_on_exit(self) -> bool:
        """Handle saving when exiting."""
        create_backup = inquirer.confirm(
            "Create backup before saving?",
            default=True
        ).execute()
        
        return self.editor.commit_changes(create_backup)


def main():
    """Main entry point."""
    try:
        cli = SaveEditorCLI()
        cli.run()
    except KeyboardInterrupt:
        rprint("\n[yellow]Exiting...[/yellow]")
    except Exception as e:
        rprint(f"[red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    main()