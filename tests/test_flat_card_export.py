from __future__ import annotations

from pathlib import Path

import pytest

from fontgallery.services.flat_card_export import FlatCardExportService
from fontgallery.services.workspace import WorkspaceService


def test_flat_card_export_copies_main_cards_into_single_root_folder(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="es_ES")
    workspace.prepare_structure()

    first = workspace.album_main_cards_dir / "fonts-alee" / "fonts-alee__Bandal.png"
    second = workspace.album_main_cards_dir / "fonts-breip" / "fonts-breip__Breip.png"
    first.parent.mkdir(parents=True, exist_ok=True)
    second.parent.mkdir(parents=True, exist_ok=True)
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    service = FlatCardExportService(workspace)
    progress_updates: list[tuple[int, int, str]] = []

    summary = service.export_album(
        "main",
        progress=lambda current, total, label: progress_updates.append((current, total, label)),
    )

    assert summary.copied_cards == 2
    assert (workspace.album_main_flat_cards_dir / "fonts-alee__Bandal.png").read_bytes() == b"first"
    assert (workspace.album_main_flat_cards_dir / "fonts-breip__Breip.png").read_bytes() == b"second"
    assert progress_updates[0][0] == 0
    assert progress_updates[-1][0] == progress_updates[-1][1]


def test_flat_card_export_fails_when_no_cards_exist(tmp_path: Path) -> None:
    workspace = WorkspaceService(tmp_path, language_code="es_ES")
    workspace.prepare_structure()
    service = FlatCardExportService(workspace)

    with pytest.raises(FileNotFoundError):
        service.export_album("main")
