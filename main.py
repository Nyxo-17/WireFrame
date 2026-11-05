"""Point d'entrée unique de l'application Wireframe V1 (compatible Python système, venv et runtime portable intégré)."""

import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Configure automatiquement Tcl/Tk si l'exécuteur portable intégré (runtime/) est utilisé
RUNTIME_TCL = ROOT_DIR / "runtime" / "tcl"
if RUNTIME_TCL.exists():
    os.environ.setdefault("TCL_LIBRARY", str(RUNTIME_TCL / "tcl8.6"))
    os.environ.setdefault("TK_LIBRARY", str(RUNTIME_TCL / "tk8.6"))

from ui.app_window import WireframeApp


def main() -> None:
    """Instancie et démarre la boucle principale de la fenêtre CustomTkinter."""
    app = WireframeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
