from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from contact_cleaner.gui_dpg.app import main

if __name__ == "__main__":
    main()
