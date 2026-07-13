from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QCoreApplication

from .workspace import WorkspaceService


FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".pfa", ".pfb"}
FONT_PACKAGE_PREFIXES = ("fonts-", "ttf-", "gsfonts", "lmodern", "cm-super", "t1-")


@dataclass(frozen=True)
class ExtractedFont:
    family: str
    style: str
    fullname: str
    package: str
    filename: str
    path: Path


@dataclass(frozen=True)
class ExtractionSummary:
    packages_seen: int
    font_packages_processed: int
    unique_fonts_extracted: int
    duplicate_fonts_skipped: int
    broken_fonts_skipped: int
    extract_dir: Path


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_font_package(path: Path) -> bool:
    return path.name.endswith(".deb") and path.name.startswith(FONT_PACKAGE_PREFIXES)


def package_base_name(path: Path) -> str:
    name = path.name[:-4]
    parts = name.rsplit("_", 2)
    return parts[0] if len(parts) == 3 else name


def scan_font(font_path: Path) -> tuple[str, str, str]:
    result = run(
        ["fc-scan", "--format", "%{family}|%{style}|%{fullname}\n", str(font_path)],
        capture_output=True,
    )
    line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    parts = [part.strip() for part in line.split("|")]
    while len(parts) < 3:
        parts.append("")
    family = parts[0].split(",")[0].strip() or font_path.stem
    style = parts[1].split(",")[0].strip() or "Regular"
    fullname = parts[2].split(",")[0].strip() or f"{family} {style}".strip()
    return family, style, fullname


class ExtractionService:
    def __init__(self, workspace: WorkspaceService) -> None:
        self.workspace = workspace

    def extract_to_main_album(
        self,
        log: Callable[[str], None] | None = None,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> tuple[ExtractionSummary, list[ExtractedFont]]:
        def emit(message: str) -> None:
            if log is not None:
                log(message)

        self.workspace.prepare_structure()
        extract_dir = self.workspace.album_main_extract_dir
        extract_dir.mkdir(parents=True, exist_ok=True)

        packages = sorted(path for path in self.workspace.packages_dir.glob("*.deb"))
        font_packages = [path for path in packages if is_font_package(path)]
        if not font_packages:
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "ExtractionService",
                    "No font .deb packages were found in: {path}",
                ).format(path=self.workspace.packages_dir)
            )

        seen_hashes: set[str] = set()
        extracted_fonts: list[ExtractedFont] = []
        duplicate_fonts_skipped = 0
        broken_fonts_skipped = 0
        total = len(font_packages)

        if progress is not None:
            progress(
                0,
                total,
                QCoreApplication.translate(
                    "ExtractionService",
                    "Starting font extraction from {count} packages",
                ).format(count=total),
            )

        for index, package in enumerate(font_packages, start=1):
            pkg_name = package_base_name(package)
            pkg_out_dir = extract_dir / pkg_name
            pkg_out_dir.mkdir(parents=True, exist_ok=True)
            emit(
                QCoreApplication.translate(
                    "ExtractionService",
                    "Processing package: {package}",
                ).format(package=pkg_name)
            )
            with tempfile.TemporaryDirectory(prefix="fontgallery-deb-", dir="/tmp") as tmp_dir:
                tmp_path = Path(tmp_dir)
                run(["dpkg-deb", "-x", str(package), str(tmp_path)])
                font_files = sorted(
                    path for path in tmp_path.rglob("*")
                    if path.is_file() and path.suffix.lower() in FONT_SUFFIXES
                )
                for font_file in font_files:
                    digest = sha256(font_file)
                    if digest in seen_hashes:
                        duplicate_fonts_skipped += 1
                        continue
                    dest_name = f"{pkg_name}__{font_file.name}"
                    dest_path = pkg_out_dir / dest_name
                    try:
                        shutil.copy2(font_file, dest_path)
                        family, style, fullname = scan_font(dest_path)
                    except Exception:
                        broken_fonts_skipped += 1
                        if dest_path.exists():
                            dest_path.unlink()
                        continue
                    seen_hashes.add(digest)
                    extracted_fonts.append(
                        ExtractedFont(
                            family=family,
                            style=style,
                            fullname=fullname,
                            package=pkg_name,
                            filename=dest_name,
                            path=dest_path,
                        )
                    )
            emit(
                QCoreApplication.translate(
                    "ExtractionService",
                    "  Accumulated fonts: {count}",
                ).format(count=len(extracted_fonts))
            )
            if progress is not None:
                progress(
                    index,
                    total,
                    QCoreApplication.translate(
                        "ExtractionService",
                        "Processed package {current}/{total}: {package}",
                    ).format(current=index, total=total, package=pkg_name),
                )

        extracted_fonts.sort(
            key=lambda item: (
                item.family.lower(),
                item.fullname.lower(),
                item.style.lower(),
                item.filename.lower(),
            )
        )

        summary = ExtractionSummary(
            packages_seen=len(packages),
            font_packages_processed=len(font_packages),
            unique_fonts_extracted=len(extracted_fonts),
            duplicate_fonts_skipped=duplicate_fonts_skipped,
            broken_fonts_skipped=broken_fonts_skipped,
            extract_dir=extract_dir,
        )
        return summary, extracted_fonts
