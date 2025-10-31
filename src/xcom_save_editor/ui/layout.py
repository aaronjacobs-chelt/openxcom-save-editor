"""
Layout management utilities for consistent UI spacing and structure.
"""

from typing import List, Optional, Any, Dict
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.console import Console, Group
from rich.padding import Padding
from rich.align import Align

from .theme import get_current_theme


class LayoutManager:
    """Manages consistent layout and spacing across the UI."""
    
    # Standard spacing constants
    PADDING_SMALL = 1
    PADDING_MEDIUM = 2
    PADDING_LARGE = 3
    
    def __init__(self, console: Console):
        self.console = console
        self.theme = get_current_theme()
    
    def create_panel(
        self, 
        content: Any, 
        title: str = None, 
        subtitle: str = None,
        style: str = "primary",
        padding: int = PADDING_SMALL
    ) -> Panel:
        """Create a consistently styled panel."""
        border_color = self.theme.get_color("border")
        title_color = self.theme.get_color(style)
        
        return Panel(
            Padding(content, padding),
            title=title,
            subtitle=subtitle,
            border_style=border_color,
        )
    
    def create_table(
        self, 
        title: str = None, 
        show_header: bool = True,
        header_style: str = "table_header"
    ) -> Table:
        """Create a consistently styled table."""
        border_color = self.theme.get_color("border")
        header_color = self.theme.get_color("accent")
        
        table = Table(
            title=title,
            border_style=border_color,
            header_style=f"{header_color} bold",
            show_header=show_header,
        )
        return table
    
    def create_info_table(self, data: Dict[str, Any], title: str = None) -> Table:
        """Create a two-column info table for key-value pairs."""
        table = self.create_table(title=title)
        table.add_column("Property", style=self.theme.get_color("secondary"))
        table.add_column("Value", style=self.theme.get_color("text"))
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        return table
    
    def create_status_panels(self, status_data: Dict[str, Dict[str, Any]]) -> Group:
        """Create a grid of status panels."""
        panels = []
        
        for category, data in status_data.items():
            # Format the content
            content_lines = []
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    content_lines.append(f"{key}: {value:,}")
                else:
                    content_lines.append(f"{key}: {value}")
            
            content = "\n".join(content_lines)
            
            # Create panel with emoji icon
            icon_map = {
                "funds": "💰",
                "research": "🔬", 
                "facilities": "🏗️",
                "production": "⚙️",
                "bases": "🏠",
                "soldiers": "👤"
            }
            
            icon = icon_map.get(category.lower(), "📊")
            panel_title = f"{icon} {category.title()}"
            
            panel = self.create_panel(
                content, 
                title=panel_title,
                style="primary"
            )
            panels.append(panel)
        
        # Arrange panels in columns (2 per row)
        rows = []
        for i in range(0, len(panels), 2):
            row_panels = panels[i:i+2]
            rows.append(Columns(row_panels))
        
        return Group(*rows)
    
    def create_breadcrumb(self, path: List[str]) -> Text:
        """Create a breadcrumb navigation trail."""
        if not path:
            return Text("")
        
        breadcrumb = Text()
        separator = Text(" › ", style=self.theme.get_color("muted"))
        
        for i, item in enumerate(path):
            if i > 0:
                breadcrumb.append_text(separator)
            
            # Last item is current location (highlighted)
            if i == len(path) - 1:
                breadcrumb.append(item, style=self.theme.get_color("accent") + " bold")
            else:
                breadcrumb.append(item, style=self.theme.get_color("muted"))
        
        return breadcrumb
    
    def create_header(self, title: str, subtitle: str = None, breadcrumb: List[str] = None) -> Group:
        """Create a consistent header section."""
        components = []
        
        # Add breadcrumb if provided
        if breadcrumb:
            components.append(self.create_breadcrumb(breadcrumb))
        
        # Main title
        title_text = Text(title, style=self.theme.get_color("primary") + " bold")
        if subtitle:
            title_text.append(f" — {subtitle}", style=self.theme.get_color("muted"))
        
        components.append(Align.center(title_text))
        
        # Add spacing
        components.append(Text(""))
        
        return Group(*components)
    
    def create_footer(self, status_message: str = None, shortcuts: Dict[str, str] = None) -> Group:
        """Create a consistent footer with status and shortcuts."""
        components = []
        
        # Add spacing
        components.append(Text(""))
        
        # Status message
        if status_message:
            status_style = self.theme.get_color("info")
            components.append(Text(status_message, style=status_style))
        
        # Keyboard shortcuts
        if shortcuts:
            shortcut_parts = []
            for key, description in shortcuts.items():
                key_style = self.theme.get_color("accent") + " bold"
                desc_style = self.theme.get_color("muted")
                shortcut_parts.append(f"[{key_style}]{key}[/] [{desc_style}]{description}[/]")
            
            shortcuts_text = "  ".join(shortcut_parts)
            components.append(Text.from_markup(shortcuts_text))
        
        return Group(*components)
    
    def format_number(self, value: int, prefix: str = "", suffix: str = "") -> str:
        """Format numbers with consistent styling."""
        formatted = f"{value:,}"
        if prefix:
            formatted = f"{prefix}{formatted}"
        if suffix:
            formatted = f"{formatted}{suffix}"
        return formatted
    
    def format_percentage(self, value: float) -> str:
        """Format percentages consistently."""
        return f"{value:.1f}%"
    
    def create_progress_text(self, current: int, total: int, label: str = "") -> str:
        """Create progress text like '5 / 10 (50%)'."""
        percentage = (current / total * 100) if total > 0 else 0
        progress_text = f"{current:,} / {total:,} ({percentage:.1f}%)"
        
        if label:
            progress_text = f"{label}: {progress_text}"
            
        return progress_text