"""
Keyboard shortcut management system.
"""

from typing import Dict, Callable, Optional, List
from dataclasses import dataclass


@dataclass
class Shortcut:
    """Represents a keyboard shortcut."""
    key: str
    action: Callable
    description: str
    context: str = "global"  # Context where this shortcut is active


class ShortcutManager:
    """Manages keyboard shortcuts across the application."""
    
    def __init__(self):
        self.shortcuts: Dict[str, Dict[str, Shortcut]] = {}
        self._register_default_shortcuts()
    
    def register(self, key: str, action: Callable, description: str, context: str = "global"):
        """Register a keyboard shortcut."""
        if context not in self.shortcuts:
            self.shortcuts[context] = {}
        
        self.shortcuts[context][key] = Shortcut(
            key=key,
            action=action,
            description=description,
            context=context
        )
    
    def get_shortcuts(self, context: str = "global") -> Dict[str, Shortcut]:
        """Get shortcuts for a specific context."""
        return self.shortcuts.get(context, {})
    
    def get_all_shortcuts(self) -> Dict[str, Dict[str, Shortcut]]:
        """Get all registered shortcuts."""
        return self.shortcuts
    
    def get_shortcut_help(self, context: str = "global") -> Dict[str, str]:
        """Get shortcut help text for display."""
        shortcuts = self.get_shortcuts(context)
        return {key: shortcut.description for key, shortcut in shortcuts.items()}
    
    def execute_shortcut(self, key: str, context: str = "global") -> bool:
        """Execute a shortcut if it exists."""
        shortcuts = self.get_shortcuts(context)
        if key in shortcuts:
            try:
                shortcuts[key].action()
                return True
            except Exception as e:
                print(f"Error executing shortcut '{key}': {e}")
                return False
        return False
    
    def _register_default_shortcuts(self):
        """Register default application shortcuts."""
        # Global shortcuts
        self.register("q", lambda: None, "Quit", "global")
        self.register("h", lambda: None, "Help", "global")
        self.register("?", lambda: None, "Show shortcuts", "global")
        self.register("b", lambda: None, "Back", "global")
        self.register("r", lambda: None, "Refresh", "global")
        
        # Menu shortcuts
        self.register("s", lambda: None, "Status", "menu")
        self.register("m", lambda: None, "Money", "menu")
        self.register("t", lambda: None, "Research (Tech)", "menu")
        self.register("a", lambda: None, "Soldiers (Agents)", "menu")
        self.register("f", lambda: None, "Facilities", "menu")
        self.register("p", lambda: None, "Production", "menu")
        self.register("i", lambda: None, "Inventory", "menu")
        self.register("u", lambda: None, "Undo", "menu")
        
        # Edit shortcuts
        self.register("c", lambda: None, "Complete all", "edit")
        self.register("1", lambda: None, "Set to 1", "edit")
        self.register("0", lambda: None, "Set to max", "edit")


# Global shortcut manager instance
_shortcut_manager = ShortcutManager()


def register_shortcut(key: str, action: Callable, description: str, context: str = "global"):
    """Register a global shortcut."""
    _shortcut_manager.register(key, action, description, context)


def get_shortcut_manager() -> ShortcutManager:
    """Get the global shortcut manager."""
    return _shortcut_manager