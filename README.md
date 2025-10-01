# OpenXCom Save Editor

A safe and comprehensive save game editor for OpenXCom Extended, specifically designed for the **X-Com Files** mod. This tool allows you to modify various aspects of your save games including money, research progress, soldier stats, base facilities, production queues, and inventory.

## ⚠️ Safety First

**ALWAYS backup your save files before using this tool!** While the editor includes built-in backup functionality, it's recommended to manually backup your saves as well.

- The tool creates automatic backups before saving changes
- All modifications are validated before writing to disk
- You can preview changes before committing them
- An undo feature allows you to reset changes before saving

## Features

### 💰 Money/Funds Management
- View current funds (current month and previous month)
- Set funds to any desired amount
- Add or subtract funds from current balance

### 🔬 Research Management
- View all active research projects with progress
- Instantly complete individual or all research projects
- See research progress as percentages

### 👤 Soldier/Agent Management
- Edit individual soldier statistics
- Set all soldiers to maximum stats (100 or custom value)
- Modify individual stats (TU, Health, Bravery, Reactions, etc.)
- View soldier details including rank, missions, and kills

### 🏗️ Facility Management
- View facilities currently under construction
- Instantly complete facility construction
- Complete all facilities or individual buildings
- Shows construction time remaining

### ⚙️ Production Management
- View active manufacturing/production items
- Instantly complete production of items
- Handle both regular and infinite production queues
- Shows production progress and assigned engineers

### 📦 Inventory Management
- Browse base inventories with item quantities
- Edit item quantities (add, remove, or set to specific amounts)
- Search for items across all bases
- View formatted item names (removes STR_ prefixes)

### 🗂️ Backup Management
- Automatic timestamped backups before saving
- List and restore from previous backups
- Manual backup creation
- Backup restoration with confirmation

## Installation

### Requirements
- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

1. **Clone or download this project**
```bash
git clone <repository-url>
cd openxcomeditor
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\\Scripts\\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

1. **Place your save file in the project directory** (or note its full path)
2. **Run the editor**
```bash
# From the project directory
python -m src.xcom_save_editor
```

3. **Follow the interactive prompts:**
   - Select your save file (`.sav` files)
   - Choose from the main menu options
   - Make your desired changes
   - Review changes before saving
   - The tool will create a backup automatically

### Command Line Interface

The editor provides an intuitive menu-driven interface:

```
📊 Show Status           - View current game state overview
💰 Edit Money/Funds      - Modify current funds
🔬 Manage Research       - Complete research projects
👤 Edit Soldiers/Agents  - Modify soldier statistics
🏗️ Manage Facilities     - Complete facility construction
⚙️ Manage Production     - Complete manufacturing items
📦 Edit Inventory        - Modify base item storage
🗂️ Backup Management     - Create/restore backups
💾 Save Changes          - Commit modifications to file
↺ Reset All Changes     - Undo all pending modifications
❌ Exit                  - Exit with unsaved changes check
```

### File Structure

OpenXCom Extended save files (`.sav`) are YAML format with two documents:
1. **Header**: Contains save metadata (name, version, mods, etc.)
2. **Game Data**: Contains the actual game state

The editor preserves this structure and only modifies the game data portion.

## Safety Features

### Automatic Backups
- Backups are created before any save operation
- Backups are timestamped (format: `SaveName_YYYYMMDD_HHMMSS.bak`)
- Stored in a `backups/` subdirectory next to your save file

### Validation
- All changes are validated before writing to disk
- Basic structure and data type validation
- Reasonable value range checking
- Error prevention for invalid modifications

### Preview and Undo
- Preview changes before committing
- Reset/undo functionality discards all pending changes
- Confirmation prompts for destructive operations

### Multi-Base Support
- Automatic detection of multiple bases
- Base selection prompts when needed
- Proper handling of base-specific data (facilities, production, inventory)

## Supported Save Formats

This tool is specifically designed for:
- **OpenXCom Extended** save files
- **X-Com Files** mod (version 3.8 tested)
- YAML format save files (`.sav` extension)

It may work with other OpenXCom Extended mods, but X-Com Files is the primary target.

## Troubleshooting

### Common Issues

**"No .sav files found"**
- Ensure your save file has a `.sav` extension
- Check that you're in the correct directory
- Use the "Browse for file" option to navigate to your save

**"Save validation failed"**
- The save file may be corrupted
- Try restoring from a backup
- Check if the file is a valid OpenXCom Extended save

**"Error loading save file"**
- Ensure the file is a valid YAML format
- Check that the file isn't currently open in another program
- Verify the file isn't corrupted

### Getting Help

If you encounter issues:
1. Check that your save file is from OpenXCom Extended
2. Ensure you're using the X-Com Files mod (or compatible mod)
3. Try creating a test save and editing that first
4. Check file permissions if you get access errors

## Development

### Project Structure
```
openxcomeditor/
├── src/xcom_save_editor/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Main entry point
│   ├── cli.py               # Command line interface
│   ├── editor.py            # Main editor controller
│   ├── game_editors/        # Individual feature managers
│   │   ├── __init__.py
│   │   ├── base_manager.py  # Common base functionality
│   │   ├── money_manager.py # Money/funds editing
│   │   ├── research_manager.py # Research management
│   │   ├── soldier_manager.py # Soldier stats editing
│   │   ├── facility_manager.py # Base facility management
│   │   ├── production_manager.py # Manufacturing management
│   │   └── inventory_manager.py # Inventory editing
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── file_ops.py      # File operations and backup
│       └── validator.py     # Save file validation
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── SaveGame.sav            # Example save file
```

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## License

This project is provided as-is for educational and personal use. Always backup your saves before using any save editing tool.

## Disclaimer

This tool modifies game save files. While every effort has been made to ensure safety and data integrity:
- Always backup your saves before editing
- Test changes on backup saves first
- The tool is designed for X-Com Files mod specifically
- Compatibility with other mods is not guaranteed
- Use at your own risk

---

**Happy X-Com commanding! 👽🛸**