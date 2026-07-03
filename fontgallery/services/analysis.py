from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QCoreApplication

from .workspace import WorkspaceService


REQUIRED_SPANISH_CODEPOINTS = {
    0x00E1,
    0x00E9,
    0x00ED,
    0x00F3,
    0x00FA,
    0x00FC,
    0x00F1,
    0x00C1,
    0x00C9,
    0x00CD,
    0x00D3,
    0x00DA,
    0x00DC,
    0x00D1,
}

TECHNICAL_KEYWORDS = (
    "jsmath",
    "latex",
    "tex",
    "lyx",
    "math",
    "mathematical",
    "equation",
    "formula",
    "symbol",
    "stmary",
    "wasy",
    "rsfs",
    "msam",
    "msbm",
    "cmex",
    "cmsy",
    "cmmi",
    "eufm",
    "eusm",
)


@dataclass(frozen=True)
class AnalyzedFont:
    family: str
    style: str
    fullname: str
    package: str
    filename: str
    path: Path
    supports_spanish: bool
    is_technical: bool


@dataclass(frozen=True)
class AnalysisSummary:
    total_fonts: int
    spanish_fonts: int
    technical_fonts: int
    copied_to_spanish: int
    copied_to_technical: int
    skipped_without_spanish: int
    copied_to_main_design: int


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def parse_charset(raw: str) -> set[int]:
    codepoints: set[int] = set()
    for token in raw.replace("\n", " ").split():
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_hex, end_hex = token.split("-", 1)
            try:
                start = int(start_hex, 16)
                end = int(end_hex, 16)
            except ValueError:
                continue
            if end < start:
                start, end = end, start
            codepoints.update(range(start, end + 1))
            continue
        try:
            codepoints.add(int(token, 16))
        except ValueError:
            continue
    return codepoints


def scan_font(font_path: Path) -> tuple[str, str, str, set[int]]:
    result = run(
        ["fc-scan", "--format", "%{family}|%{style}|%{fullname}|%{charset}\n", str(font_path)],
        capture_output=True,
    )
    line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    parts = [part.strip() for part in line.split("|", 3)]
    while len(parts) < 4:
        parts.append("")
    family = parts[0].split(",")[0].strip() or font_path.stem
    style = parts[1].split(",")[0].strip() or "Regular"
    fullname = parts[2].split(",")[0].strip() or f"{family} {style}".strip()
    charset = parse_charset(parts[3])
    return family, style, fullname, charset


class AnalysisService:
    def __init__(self, workspace: WorkspaceService) -> None:
        self.workspace = workspace

    def analyze_main_collection(
        self,
        log: Callable[[str], None] | None = None,
    ) -> tuple[AnalysisSummary, list[AnalyzedFont]]:
        def emit(message: str) -> None:
            if log is not None:
                log(message)

        source_dir = self.workspace.album_main_extract_dir
        if not source_dir.exists():
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "AnalysisService",
                    "The extracted master collection does not exist: {path}",
                ).format(path=source_dir)
            )

        font_paths = sorted(path for path in source_dir.rglob("*") if path.is_file())
        if not font_paths:
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "AnalysisService",
                    "No extracted fonts were found in: {path}",
                ).format(path=source_dir)
            )

        analyzed: list[AnalyzedFont] = []
        spanish_count = 0
        technical_count = 0

        for font_path in font_paths:
            family, style, fullname, charset = scan_font(font_path)
            package = font_path.parent.name
            supports_spanish = REQUIRED_SPANISH_CODEPOINTS.issubset(charset)
            is_technical = self._is_technical_font(package, family, style, fullname, font_path.name)
            analyzed.append(
                AnalyzedFont(
                    family=family,
                    style=style,
                    fullname=fullname,
                    package=package,
                    filename=font_path.name,
                    path=font_path,
                    supports_spanish=supports_spanish,
                    is_technical=is_technical,
                )
            )
            spanish_count += int(supports_spanish)
            technical_count += int(is_technical)

        analyzed.sort(
            key=lambda item: (
                item.family.lower(),
                item.fullname.lower(),
                item.style.lower(),
                item.filename.lower(),
            )
        )

        copied_spanish = self._copy_subset(
            [font for font in analyzed if font.supports_spanish and not font.is_technical],
            self.workspace.album_es_extract_dir,
            emit,
            self.workspace.album_es_dir.name,
        )
        copied_technical = self._copy_subset(
            [font for font in analyzed if font.is_technical],
            self.workspace.album_tech_extract_dir,
            emit,
            self.workspace.album_tech_dir.name,
        )

        summary = AnalysisSummary(
            total_fonts=len(analyzed),
            spanish_fonts=spanish_count,
            technical_fonts=technical_count,
            copied_to_spanish=copied_spanish,
            copied_to_technical=copied_technical,
            skipped_without_spanish=len(analyzed) - spanish_count,
            copied_to_main_design=len([font for font in analyzed if not font.is_technical]),
        )
        return summary, analyzed

    def _copy_subset(
        self,
        fonts: list[AnalyzedFont],
        target_dir: Path,
        emit: Callable[[str], None],
        label: str,
    ) -> int:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        for font in fonts:
            package_dir = target_dir / font.package
            package_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(font.path, package_dir / font.filename)

        emit(
            QCoreApplication.translate(
                "AnalysisService",
                "Copied {count} fonts to {label}",
            ).format(count=len(fonts), label=label)
        )
        return len(fonts)

    def _is_technical_font(
        self,
        package: str,
        family: str,
        style: str,
        fullname: str,
        filename: str,
    ) -> bool:
        haystack = " ".join((package, family, style, fullname, filename)).lower()
        return any(keyword in haystack for keyword in TECHNICAL_KEYWORDS)
