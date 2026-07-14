from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QCoreApplication

from .workspace import WorkspaceService


@dataclass(frozen=True)
class FlatCardExportSummary:
    label: str
    source_dir: Path
    output_dir: Path
    copied_cards: int


class FlatCardExportService:
    def __init__(self, workspace: WorkspaceService) -> None:
        self.workspace = workspace

    def export_album(
        self,
        label: str,
        log: Callable[[str], None] | None = None,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> FlatCardExportSummary:
        albums = {
            "main": (self.workspace.album_main_cards_dir, self.workspace.album_main_flat_cards_dir),
            "spanish": (self.workspace.album_es_cards_dir, self.workspace.album_es_flat_cards_dir),
            "technical": (self.workspace.album_tech_cards_dir, self.workspace.album_tech_flat_cards_dir),
        }
        if label not in albums:
            raise ValueError(f"Unsupported album label: {label}")

        source_dir, output_dir = albums[label]
        png_paths = sorted(path for path in source_dir.rglob("*.png") if path.is_file())
        if not png_paths:
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "FlatCardExportService",
                    "No PNG cards were found in: {path}",
                ).format(path=source_dir)
            )

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        total = len(png_paths)
        if progress is not None:
            progress(
                0,
                total,
                QCoreApplication.translate(
                    "FlatCardExportService",
                    "Starting flat PNG export for the {label} album",
                ).format(label=label),
            )

        for index, png_path in enumerate(png_paths, start=1):
            shutil.copy2(png_path, output_dir / png_path.name)
            if progress is not None:
                progress(
                    index,
                    total,
                    QCoreApplication.translate(
                        "FlatCardExportService",
                        "Copied flat card {current}/{total}: {file}",
                    ).format(current=index, total=total, file=png_path.name),
                )

        if log is not None:
            log(
                QCoreApplication.translate(
                    "FlatCardExportService",
                    "Copied {count} PNG cards into the flat folder: {path}",
                ).format(count=total, path=output_dir)
            )

        return FlatCardExportSummary(
            label=label,
            source_dir=source_dir,
            output_dir=output_dir,
            copied_cards=total,
        )
