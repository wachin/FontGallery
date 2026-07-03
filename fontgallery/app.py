from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QLocale, QTranslator
from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow
from .services.workspace import WorkspaceService, normalize_language


def load_translator(app: QApplication, project_root: Path, locale_name: str) -> QTranslator | None:
    language = normalize_language(locale_name)
    translations_dir = project_root / "translations"
    qm_path = translations_dir / f"fontgallery_{language}.qm"
    if not qm_path.exists():
        return None

    translator = QTranslator(app)
    if not translator.load(str(qm_path)):
        return None

    app.installTranslator(translator)
    return translator


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FontGallery")
    app.setOrganizationName("FontGallery")

    project_root = Path.cwd()
    locale_name = QLocale.system().name()
    translator = load_translator(app, project_root, locale_name)
    workspace = WorkspaceService(project_root, language_code=locale_name)
    window = MainWindow(workspace)
    window._translator = translator  # Keep translator alive for the lifetime of the application.
    window.show()
    return app.exec()
