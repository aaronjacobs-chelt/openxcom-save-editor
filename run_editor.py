#!/usr/bin/env python3
"""
Simple runner script for the OpenXCom Save Editor.

This script makes it easy to run the editor without having to remember
the module path syntax.
"""

import sys
from pathlib import Path

# Add src to path so we can import the module
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from xcom_save_editor.cli import main

if __name__ == "__main__":
    main()