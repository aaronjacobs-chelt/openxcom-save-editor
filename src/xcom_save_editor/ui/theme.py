"""
Theme management system for the OpenXCom Save Editor UI.
"""

from typing import Dict, Any, Optional
from rich.theme import Theme as RichTheme
from rich.style import Style
from pathlib import Path
import json


class Theme:
    """Manages UI themes and styling."""
    
    THEMES = {
        "default": {
            "primary": "#00ff00",      # Bright green (classic terminal)
            "secondary": "#00ffff",    # Cyan
            "accent": "#ffff00",       # Yellow
            "success": "#00ff00",      # Green
            "warning": "#ffaa00",      # Orange
            "error": "#ff0000",        # Red
            "info": "#00aaff",         # Blue
            "text": "#ffffff",         # White
            "muted": "#808080",        # Gray
            "background": "#000000",   # Black
            "border": "#444444",       # Dark gray
        },
        
        "dark": {
            "primary": "#61dafb",      # React blue
            "secondary": "#bb86fc",    # Purple
            "accent": "#03dac6",       # Teal
            "success": "#4caf50",      # Material green
            "warning": "#ff9800",      # Material orange
            "error": "#f44336",        # Material red
            "info": "#2196f3",         # Material blue
            "text": "#e0e0e0",         # Light gray
            "muted": "#757575",        # Medium gray
            "background": "#121212",   # Very dark gray
            "border": "#333333",       # Dark border
        },
        
        "light": {
            "primary": "#1976d2",      # Blue
            "secondary": "#7b1fa2",    # Purple
            "accent": "#00796b",       # Teal
            "success": "#388e3c",      # Green
            "warning": "#f57c00",      # Orange
            "error": "#d32f2f",        # Red
            "info": "#1976d2",         # Blue
            "text": "#212121",         # Dark gray
            "muted": "#757575",        # Medium gray
            "background": "#ffffff",   # White
            "border": "#e0e0e0",       # Light border
        },
        
        "cyberpunk": {
            "primary": "#ff00ff",      # Magenta
            "secondary": "#00ffff",    # Cyan
            "accent": "#ffff00",       # Yellow
            "success": "#00ff41",      # Neon green
            "warning": "#ff9f00",      # Neon orange
            "error": "#ff073a",        # Neon red
            "info": "#0abdc6",         # Neon cyan
            "text": "#ffffff",         # White
            "muted": "#888888",        # Gray
            "background": "#0d1117",   # Very dark
            "border": "#30363d",       # Dark border
        }
    }
    
    def __init__(self, theme_name: str = "default"):
        self.theme_name = theme_name
        self._colors = self.THEMES.get(theme_name, self.THEMES["default"])
        self._rich_theme = self._create_rich_theme()
    
    def _create_rich_theme(self) -> RichTheme:
        """Create a Rich theme from our color palette."""
        styles = {}
        
        # Map our semantic colors to Rich styles
        for key, color in self._colors.items():
            styles[key] = Style(color=color)
        
        # Additional style combinations
        styles["panel_title"] = Style(color=self._colors["primary"], bold=True)
        styles["table_header"] = Style(color=self._colors["accent"], bold=True)
        styles["menu_item"] = Style(color=self._colors["text"])
        styles["menu_highlight"] = Style(color=self._colors["accent"], bold=True)
        styles["status_changed"] = Style(color=self._colors["warning"], italic=True)
        styles["status_saved"] = Style(color=self._colors["success"], bold=True)
        
        return RichTheme(styles)
    
    def get_color(self, key: str) -> str:
        """Get a color value by key."""
        return self._colors.get(key, self._colors["text"])
    
    def get_style(self, key: str) -> Style:
        """Get a Rich style by key."""
        return self._rich_theme.styles.get(key, Style())
    
    @property
    def rich_theme(self) -> RichTheme:
        """Get the Rich theme object."""
        return self._rich_theme
    
    def styled(self, text: str, style_key: str) -> str:
        """Apply a style to text using Rich markup."""
        color = self.get_color(style_key)
        return f"[{color}]{text}[/{color}]"


# Global theme management
_current_theme: Optional[Theme] = None
_config_file = Path.home() / ".openxcom_editor" / "config.json"


def get_current_theme() -> Theme:
    """Get the currently active theme."""
    global _current_theme
    if _current_theme is None:
        # Load from config or use default
        theme_name = _load_theme_from_config()
        _current_theme = Theme(theme_name)
    return _current_theme


def set_theme(theme_name: str) -> bool:
    """Set the active theme and save to config."""
    global _current_theme
    
    if theme_name not in Theme.THEMES:
        return False
    
    _current_theme = Theme(theme_name)
    _save_theme_to_config(theme_name)
    return True


def get_available_themes() -> list[str]:
    """Get list of available theme names."""
    return list(Theme.THEMES.keys())


def _load_theme_from_config() -> str:
    """Load theme preference from config file."""
    try:
        if _config_file.exists():
            with open(_config_file, 'r') as f:
                config = json.load(f)
                return config.get('theme', 'default')
    except Exception:
        pass
    return 'default'


def _save_theme_to_config(theme_name: str) -> None:
    """Save theme preference to config file."""
    try:
        _config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {}
        if _config_file.exists():
            with open(_config_file, 'r') as f:
                config = json.load(f)
        
        config['theme'] = theme_name
        
        with open(_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass  # Fail silently if we can't save config