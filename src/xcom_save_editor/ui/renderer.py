"""
UI Renderer that provides a consistent abstraction layer for all interface elements.
"""

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from .theme import get_current_theme
from .layout import LayoutManager


class UIRenderer:
    """Central renderer for all UI elements."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.theme = get_current_theme()
        self.layout_manager = LayoutManager(self.console)
        self.breadcrumb_stack: List[str] = []
        
        # Apply theme to console
        self.console.push_theme(self.theme.rich_theme)
    
    def push_breadcrumb(self, item: str):
        """Add an item to the breadcrumb trail."""
        self.breadcrumb_stack.append(item)
    
    def pop_breadcrumb(self) -> Optional[str]:
        """Remove and return the last breadcrumb item."""
        return self.breadcrumb_stack.pop() if self.breadcrumb_stack else None
    
    def clear_breadcrumbs(self):
        """Clear the entire breadcrumb trail."""
        self.breadcrumb_stack.clear()
    
    def print(self, *args, **kwargs):
        """Themed print wrapper."""
        self.console.print(*args, **kwargs)
    
    def render_welcome_screen(self, title: str = "OpenXCom Save Editor", subtitle: str = None):
        """Render the welcome screen."""
        header = self.layout_manager.create_header(
            title=title,
            subtitle=subtitle or "Edit your X-Com Files saves safely"
        )
        self.console.print(header)
    
    def render_save_info(self, save_info: Dict[str, Any]):
        """Render save file information in a table."""
        # Format data for display
        formatted_info = {}
        
        for key, value in save_info.items():
            if key == 'size' and isinstance(value, int):
                formatted_info['File Size'] = f"{value:,} bytes"
            elif key == 'base_names' and isinstance(value, list):
                formatted_info['Bases'] = ", ".join(value)
            else:
                # Convert snake_case to Title Case
                display_key = key.replace('_', ' ').title()
                formatted_info[display_key] = str(value)
        
        table = self.layout_manager.create_info_table(
            data=formatted_info,
            title="Save Game Information"
        )
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def render_status_dashboard(self, status_data: Dict[str, Dict[str, Any]]):
        """Render the status dashboard with panels."""
        panels = self.layout_manager.create_status_panels(status_data)
        self.console.print()
        self.console.print(panels)
        self.console.print()
    
    def render_changes_status(self, has_changes: bool):
        """Render the changes status indicator."""
        if has_changes:
            status_text = self.theme.styled("⚠ You have unsaved changes", "warning")
        else:
            status_text = self.theme.styled("✓ No unsaved changes", "success")
        
        self.console.print(status_text)
        self.console.print()
    
    def render_header_with_breadcrumb(self, current_section: str, subtitle: str = None):
        """Render a section header with breadcrumb navigation."""
        header = self.layout_manager.create_header(
            title=current_section,
            subtitle=subtitle,
            breadcrumb=self.breadcrumb_stack + [current_section]
        )
        self.console.print(header)
    
    def render_success_message(self, message: str):
        """Render a success message."""
        styled_msg = self.theme.styled(f"✓ {message}", "success")
        self.console.print(styled_msg)
    
    def render_warning_message(self, message: str):
        """Render a warning message."""
        styled_msg = self.theme.styled(f"⚠ {message}", "warning")
        self.console.print(styled_msg)
    
    def render_error_message(self, message: str):
        """Render an error message."""
        styled_msg = self.theme.styled(f"✗ {message}", "error")
        self.console.print(styled_msg)
    
    def render_info_message(self, message: str):
        """Render an info message."""
        styled_msg = self.theme.styled(f"ℹ {message}", "info")
        self.console.print(styled_msg)
    
    def render_table_with_data(self, data: List[Dict[str, Any]], title: str = None, columns: List[str] = None):
        """Render a data table with consistent styling."""
        if not data:
            self.render_warning_message(f"No {title.lower() if title else 'data'} found.")
            return
        
        table = self.layout_manager.create_table(title=title)
        
        # Auto-detect columns if not provided
        if not columns and data:
            columns = list(data[0].keys())
        
        # Add columns
        for col in columns:
            display_name = col.replace('_', ' ').title()
            table.add_column(display_name, style=self.theme.get_color("text"))
        
        # Add rows
        for row in data:
            table.add_row(*[str(row.get(col, "")) for col in columns])
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def render_progress_info(self, items: List[Any], item_formatter=None):
        """Render a list of items with progress information."""
        if not items:
            return
        
        table = self.layout_manager.create_table()
        table.add_column("Item", style=self.theme.get_color("text"))
        table.add_column("Progress", style=self.theme.get_color("secondary"))
        
        for item in items:
            if item_formatter:
                name, progress = item_formatter(item)
            else:
                name = str(item)
                progress = "Unknown"
            
            table.add_row(name, progress)
        
        self.console.print(table)
        self.console.print()
    
    def render_footer(self, status: str = None, shortcuts: Dict[str, str] = None):
        """Render a footer with status and shortcuts."""
        footer = self.layout_manager.create_footer(
            status_message=status,
            shortcuts=shortcuts
        )
        self.console.print(footer)
    
    def clear_screen(self):
        """Clear the screen."""
        self.console.clear()
    
    def set_theme(self, theme_name: str) -> bool:
        """Change the active theme."""
        from .theme import set_theme
        
        if set_theme(theme_name):
            # Update our references
            self.theme = get_current_theme()
            self.layout_manager.theme = self.theme
            
            # Apply new theme to console
            self.console._theme_stack.clear()
            self.console.push_theme(self.theme.rich_theme)
            return True
        return False
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        from .theme import get_available_themes
        return get_available_themes()
    
    def format_item_count(self, current: int, total: int = None) -> str:
        """Format item counts consistently."""
        if total is not None:
            return f"{current:,} / {total:,}"
        else:
            return f"{current:,}"
    
    def format_currency(self, amount: int) -> str:
        """Format currency amounts consistently."""
        return f"${amount:,}"