"""
Enhanced prompt utilities with keyboard shortcut support.
"""

from typing import Dict, List, Any, Optional, Callable
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.prompts import ListPrompt
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings


class ShortcutSelectPrompt:
    """Select prompt with keyboard shortcut support."""
    
    def __init__(
        self, 
        message: str,
        choices: List[Dict[str, Any]], 
        shortcuts: Dict[str, str] = None
    ):
        self.message = message
        self.choices = choices
        self.shortcuts = shortcuts or {}
        self.shortcut_actions = {}
        
        # Map shortcuts to choice values
        for key, action_name in self.shortcuts.items():
            for choice in choices:
                if choice["name"].lower().find(action_name.lower()) != -1:
                    self.shortcut_actions[key] = choice["value"]
                    break
    
    def execute(self) -> str:
        """Execute the prompt with shortcut support."""
        # Create custom keybindings
        bindings = KeyBindings()
        result = {"value": None, "completed": False}
        
        def make_shortcut_handler(action_value):
            def handler(event):
                result["value"] = action_value
                result["completed"] = True
                event.app.exit(result=action_value)
            return handler
        
        # Register shortcuts
        for key, action_value in self.shortcut_actions.items():
            bindings.add(key)(make_shortcut_handler(action_value))
        
        # Special shortcuts
        bindings.add('q')(make_shortcut_handler("exit"))
        bindings.add('h')(make_shortcut_handler("help"))
        
        # Create the prompt with custom keybindings
        prompt = inquirer.select(
            message=self.message,
            choices=self.choices,
            keybindings=bindings,
        )
        
        try:
            return prompt.execute()
        except KeyboardInterrupt:
            return "exit"


def enhanced_select(
    message: str, 
    choices: List[Dict[str, Any]], 
    shortcuts: Dict[str, str] = None
) -> str:
    """Enhanced select with keyboard shortcuts."""
    prompt = ShortcutSelectPrompt(message, choices, shortcuts)
    return prompt.execute()


def create_menu_choices_with_shortcuts(menu_items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Create menu choices with keyboard shortcuts indicated."""
    choices = []
    
    for item in menu_items:
        name = item["name"]
        value = item["value"]
        shortcut = item.get("shortcut")
        
        if shortcut:
            name = f"[{shortcut.upper()}] {name}"
        
        choices.append({"name": name, "value": value})
    
    return choices


# Convenience functions for common prompt patterns
def quick_confirm(message: str, default: bool = True) -> bool:
    """Quick confirmation prompt."""
    return inquirer.confirm(message=message, default=default).execute()


def quick_text(message: str, default: str = "") -> str:
    """Quick text input prompt."""
    return inquirer.text(message=message, default=default).execute()


def quick_number(
    message: str, 
    default: int = 0, 
    min_allowed: int = None, 
    max_allowed: int = None
) -> int:
    """Quick number input prompt."""
    return inquirer.number(
        message=message,
        default=default,
        min_allowed=min_allowed,
        max_allowed=max_allowed
    ).execute()