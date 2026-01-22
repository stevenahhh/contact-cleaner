from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from contact_cleaner.gui_dpg.app import main

if __name__ == "__main__":
    main()
