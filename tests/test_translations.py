from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QCoreApplication

from fontgallery.app import load_translator


def test_spanish_translator_loads(qapp) -> None:
    translator = load_translator(qapp, Path.cwd(), "es_ES")

    assert translator is not None


def test_spanish_translates_main_window_string(qapp) -> None:
    translator = load_translator(qapp, Path.cwd(), "es_ES")

    assert translator is not None
    assert QCoreApplication.translate("MainWindow", "Workspace Status") == "Estado del espacio de trabajo"


def test_spanish_translates_service_string(qapp) -> None:
    translator = load_translator(qapp, Path.cwd(), "es_ES")

    assert translator is not None
    translated = QCoreApplication.translate(
        "ExtractionService",
        "Processing package: {package}",
    ).format(package="fonts-demo")
    assert translated == "Procesando paquete: fonts-demo"
