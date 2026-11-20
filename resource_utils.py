from pathlib import Path
import sys

def resource_path(relative):
    path = Path(relative)
    if path.is_absolute():
        return path
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS) # type: ignore
    else:
        base = Path(__file__).resolve().parent
        if base.name == "src":
            base = base.parent
    return base / path