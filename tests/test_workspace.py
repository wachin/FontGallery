from __future__ import annotations

from pathlib import Path

from fontgallery.services.workspace import WorkspaceService


def test_workspace_creates_english_structure_in_empty_directory(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="en_US")

    created = workspace.prepare_structure()

    assert {path.name for path in created} == {
        "deb-packages",
        "font-album",
        "spanish-font-album",
        "technical-font-album",
    }
    assert workspace.packages_dir.name == "deb-packages"
    assert workspace.album_main_dir.name == "font-album"
    assert workspace.album_es_dir.name == "spanish-font-album"
    assert workspace.album_tech_dir.name == "technical-font-album"


def test_workspace_creates_spanish_structure_in_empty_directory(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="es_ES")

    created = workspace.prepare_structure()

    assert {path.name for path in created} == {
        "paquetes-deb",
        "album-fuentes",
        "album-fuentes-espanol",
        "album-fuentes-tecnicas",
    }
    assert workspace.packages_dir.name == "paquetes-deb"
    assert workspace.album_main_dir.name == "album-fuentes"
    assert workspace.album_es_dir.name == "album-fuentes-espanol"
    assert workspace.album_tech_dir.name == "album-fuentes-tecnicas"


def test_workspace_reuses_existing_spanish_structure_for_english_locale(tmp_path: Path) -> None:
    for dirname in (
        "paquetes-deb",
        "album-fuentes",
        "album-fuentes-espanol",
        "album-fuentes-tecnicas",
    ):
        (tmp_path / dirname).mkdir(parents=True, exist_ok=True)

    workspace = WorkspaceService(tmp_path, language_code="en_US")

    assert workspace.packages_dir.name == "paquetes-deb"
    assert workspace.album_main_dir.name == "album-fuentes"
    assert workspace.album_es_dir.name == "album-fuentes-espanol"
    assert workspace.album_tech_dir.name == "album-fuentes-tecnicas"
