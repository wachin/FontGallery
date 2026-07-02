from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow
from .services.workspace import WorkspaceService


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FontGallery")
    app.setOrganizationName("FontGallery")

    project_root = Path.cwd()
    workspace = WorkspaceService(project_root)
    window = MainWindow(workspace)
    window.show()
    return app.exec()
