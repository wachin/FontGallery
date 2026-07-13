from __future__ import annotations

import os
from pathlib import Path

from fontgallery.services.workspace import WorkspaceService


def test_workspace_creates_english_structure_in_empty_directory(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="en_US")

    created = workspace.prepare_structure()

    assert {path.relative_to(tmp_path).as_posix() for path in created} == {
        "deb-packages",
        "font-album",
        "font-album/font-cards",
        "font-album/extracted-fonts",
        "spanish-font-album",
        "spanish-font-album/spanish-font-cards",
        "spanish-font-album/extracted-fonts",
        "technical-font-album",
        "technical-font-album/technical-font-cards",
        "technical-font-album/extracted-fonts",
    }
    assert workspace.packages_dir.name == "deb-packages"
    assert workspace.album_main_dir.name == "font-album"
    assert workspace.album_es_dir.name == "spanish-font-album"
    assert workspace.album_tech_dir.name == "technical-font-album"
    assert workspace.album_main_extract_dir.is_dir()
    assert workspace.album_es_extract_dir.is_dir()
    assert workspace.album_tech_extract_dir.is_dir()
    assert workspace.album_main_cards_dir.name == "font-cards"
    assert workspace.album_es_cards_dir.name == "spanish-font-cards"
    assert workspace.album_tech_cards_dir.name == "technical-font-cards"


def test_workspace_creates_spanish_structure_in_empty_directory(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="es_ES")

    created = workspace.prepare_structure()

    assert {path.relative_to(tmp_path).as_posix() for path in created} == {
        "paquetes-deb",
        "album-fuentes",
        "album-fuentes/fuentes-extraidas",
        "album-fuentes/tarjetas-fuentes",
        "album-fuentes-espanol",
        "album-fuentes-espanol/fuentes-extraidas",
        "album-fuentes-espanol/tarjetas-fuentes-espanol",
        "album-fuentes-tecnicas",
        "album-fuentes-tecnicas/fuentes-extraidas",
        "album-fuentes-tecnicas/tarjetas-fuentes-tecnicas",
    }
    assert workspace.packages_dir.name == "paquetes-deb"
    assert workspace.album_main_dir.name == "album-fuentes"
    assert workspace.album_es_dir.name == "album-fuentes-espanol"
    assert workspace.album_tech_dir.name == "album-fuentes-tecnicas"
    assert workspace.album_main_cards_dir.name == "tarjetas-fuentes"
    assert workspace.album_es_cards_dir.name == "tarjetas-fuentes-espanol"
    assert workspace.album_tech_cards_dir.name == "tarjetas-fuentes-tecnicas"


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
    assert workspace.album_main_cards_dir.name == "tarjetas-fuentes"
    assert workspace.album_es_cards_dir.name == "tarjetas-fuentes-espanol"
    assert workspace.album_tech_cards_dir.name == "tarjetas-fuentes-tecnicas"


def test_workspace_status_reports_missing_paths_as_writable_when_parent_is_writable(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="en_US")

    status_by_key = {item["key"]: item for item in workspace.path_status()}

    assert status_by_key["packages"]["exists"] is False
    assert status_by_key["packages"]["writable"] is True
    assert status_by_key["album_main"]["exists"] is False
    assert status_by_key["album_main"]["writable"] is True


def test_workspace_prepare_structure_fails_when_parent_is_not_writable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace = WorkspaceService(tmp_path, language_code="en_US")

    original_access = os.access

    def fake_access(path: os.PathLike[str] | str, mode: int) -> bool:
        if Path(path) == tmp_path and mode == os.W_OK | os.X_OK:
            return False
        return original_access(path, mode)

    monkeypatch.setattr("fontgallery.services.workspace.os.access", fake_access)

    try:
        workspace.prepare_structure()
    except PermissionError as exc:
        assert str(tmp_path) in str(exc)
    else:
        raise AssertionError("Expected workspace preparation to fail when the project root is not writable")


def test_workspace_prepare_structure_reports_progress(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="es_ES")
    progress_updates: list[tuple[int, int, str]] = []

    workspace.prepare_structure(progress=lambda current, total, label: progress_updates.append((current, total, label)))

    assert progress_updates
    assert len(progress_updates) == len(workspace.required_directories)
    assert progress_updates[-1][0] == progress_updates[-1][1]
