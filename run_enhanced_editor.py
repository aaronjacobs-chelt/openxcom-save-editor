#!/usr/bin/env python3
"""
Enhanced OpenXCom Save Editor entry point.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import the modules
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    from xcom_save_editor.enhanced_cli import main
    main()