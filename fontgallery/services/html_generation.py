from __future__ import annotations

import html
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QCoreApplication

from .analysis import TECHNICAL_KEYWORDS
from .workspace import WorkspaceService


DEFAULT_SAMPLE_TEXT = (
    "abcdefghijklmnopqrstuvwxyz\n"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
    "0123456789 áéíóú üñ |@#~½{[]}¡!\"'$%&\\ /()=¿?<> +-ºª÷©°®\n"
    "\"Nunca se aparten de ti la misericordia y la verdad;\n"
    "átalas a tu cuello, escríbelas en la tabla de tu corazón;\n"
    "y hallarás gracia y buena opinión ante los ojos de Dios\n"
    "y de los hombres.\"\n"
    "Proverbios 3:3-4 (RVR1960)"
)

TECHNICAL_SAMPLE_TEXT = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
    "abcdefghijklmnopqrstuvwxyz\n"
    "0123456789\n"
    "+ - = / \\ ( ) [ ] { } < >\n"
    "sum integral product union intersection\n"
    "alpha beta gamma delta epsilon lambda pi sigma omega\n"
    "Technical font for mathematics, symbols, or TeX composition."
)

FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".pfa", ".pfb"}


@dataclass(frozen=True)
class HtmlFontEntry:
    family: str
    style: str
    fullname: str
    package: str
    filename: str
    path: Path
    relative_font_path: str


@dataclass(frozen=True)
class HtmlAlbumSummary:
    label: str
    html_path: Path
    included_fonts: int
    excluded_fonts: int
    excluded_report: Path | None = None


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


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


class HtmlGenerationService:
    def __init__(self, workspace: WorkspaceService) -> None:
        self.workspace = workspace

    def generate_all_albums(
        self,
        log: Callable[[str], None] | None = None,
    ) -> list[HtmlAlbumSummary]:
        def emit(message: str) -> None:
            if log is not None:
                log(message)

        self.workspace.prepare_structure()

        summaries = [
            self._generate_main_album(emit),
            self._generate_spanish_album(emit),
            self._generate_technical_album(emit),
        ]
        return summaries

    def _generate_main_album(self, emit: Callable[[str], None]) -> HtmlAlbumSummary:
        output_dir = self.workspace.album_main_dir
        source_dir = self.workspace.album_main_extract_dir
        html_path = self.workspace.album_main_html_path
        excluded_path = output_dir / "excluded-technical-fonts.txt"

        entries, excluded = self._collect_entries(
            source_dir=source_dir,
            output_dir=output_dir,
            include_technical=False,
        )
        title = QCoreApplication.translate("HtmlGenerationService", "Album of extracted fonts from .deb packages")
        intro = QCoreApplication.translate(
            "HtmlGenerationService",
            "Generated from locally extracted font packages and intended for general graphic design browsing. "
            "Technical and math-oriented fonts are excluded from this main album.",
        )
        self._write_html(
            entries=entries,
            html_path=html_path,
            title=title,
            intro=intro,
            sample_text=DEFAULT_SAMPLE_TEXT,
        )

        excluded_lines = [
            QCoreApplication.translate("HtmlGenerationService", "Technical fonts excluded from the main design album:"),
            "",
        ]
        excluded_lines.extend(
            f"- {family} | {fullname} | {style} | {package} | {filename} | {reason}"
            for family, fullname, style, package, filename, reason in excluded
        )
        excluded_path.write_text("\n".join(excluded_lines), encoding="utf-8")
        emit(
            QCoreApplication.translate(
                "HtmlGenerationService",
                "Generated main HTML album: {path}",
            ).format(path=html_path)
        )
        return HtmlAlbumSummary(
            label="main",
            html_path=html_path,
            included_fonts=len(entries),
            excluded_fonts=len(excluded),
            excluded_report=excluded_path,
        )

    def _generate_spanish_album(self, emit: Callable[[str], None]) -> HtmlAlbumSummary:
        output_dir = self.workspace.album_es_dir
        source_dir = self.workspace.album_es_extract_dir
        html_path = self.workspace.album_es_html_path

        entries, excluded = self._collect_entries(
            source_dir=source_dir,
            output_dir=output_dir,
            include_technical=True,
        )
        title = QCoreApplication.translate("HtmlGenerationService", "Album of fonts with Spanish support")
        intro = QCoreApplication.translate(
            "HtmlGenerationService",
            "Generated from the derived Spanish-support subset. "
            "These fonts are intended to cover accented Spanish characters and related glyphs.",
        )
        self._write_html(
            entries=entries,
            html_path=html_path,
            title=title,
            intro=intro,
            sample_text=DEFAULT_SAMPLE_TEXT,
        )
        emit(
            QCoreApplication.translate(
                "HtmlGenerationService",
                "Generated Spanish HTML album: {path}",
            ).format(path=html_path)
        )
        return HtmlAlbumSummary(
            label="spanish",
            html_path=html_path,
            included_fonts=len(entries),
            excluded_fonts=len(excluded),
        )

    def _generate_technical_album(self, emit: Callable[[str], None]) -> HtmlAlbumSummary:
        output_dir = self.workspace.album_tech_dir
        source_dir = self.workspace.album_tech_extract_dir
        html_path = self.workspace.album_tech_html_path

        entries, excluded = self._collect_entries(
            source_dir=source_dir,
            output_dir=output_dir,
            include_technical=True,
        )
        title = QCoreApplication.translate("HtmlGenerationService", "Album of technical and mathematical fonts")
        intro = QCoreApplication.translate(
            "HtmlGenerationService",
            "Generated for technical, mathematical, symbolic, or TeX-oriented fonts separated from the main "
            "design-focused album.",
        )
        self._write_html(
            entries=entries,
            html_path=html_path,
            title=title,
            intro=intro,
            sample_text=TECHNICAL_SAMPLE_TEXT,
        )
        emit(
            QCoreApplication.translate(
                "HtmlGenerationService",
                "Generated technical HTML album: {path}",
            ).format(path=html_path)
        )
        return HtmlAlbumSummary(
            label="technical",
            html_path=html_path,
            included_fonts=len(entries),
            excluded_fonts=len(excluded),
        )

    def _collect_entries(
        self,
        source_dir: Path,
        output_dir: Path,
        include_technical: bool,
    ) -> tuple[list[HtmlFontEntry], list[tuple[str, str, str, str, str, str]]]:
        if not source_dir.exists():
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "HtmlGenerationService",
                    "Missing extracted-font directory: {path}",
                ).format(path=source_dir)
            )

        font_paths = sorted(
            path for path in source_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in FONT_SUFFIXES
        )
        if not font_paths:
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "HtmlGenerationService",
                    "No extracted fonts were found in: {path}",
                ).format(path=source_dir)
            )

        entries: list[HtmlFontEntry] = []
        excluded: list[tuple[str, str, str, str, str, str]] = []

        for font_path in font_paths:
            family, style, fullname = scan_font(font_path)
            package = font_path.parent.name
            is_technical = self._is_technical_font(
                package=package,
                family=family,
                style=style,
                fullname=fullname,
                filename=font_path.name,
            )
            if not include_technical and is_technical:
                excluded.append(
                    (
                        family,
                        fullname,
                        style,
                        package,
                        font_path.name,
                        QCoreApplication.translate(
                            "HtmlGenerationService",
                            "Classified as technical or mathematical",
                        ),
                    )
                )
                continue

            entries.append(
                HtmlFontEntry(
                    family=family,
                    style=style,
                    fullname=fullname,
                    package=package,
                    filename=font_path.name,
                    path=font_path,
                    relative_font_path=os.path.relpath(font_path, output_dir),
                )
            )

        entries.sort(
            key=lambda item: (
                item.family.lower(),
                item.fullname.lower(),
                item.style.lower(),
                item.filename.lower(),
            )
        )
        return entries, excluded

    def _write_html(
        self,
        entries: list[HtmlFontEntry],
        html_path: Path,
        title: str,
        intro: str,
        sample_text: str,
    ) -> None:
        html_path.write_text(
            self._html_document(entries, title, intro, sample_text),
            encoding="utf-8",
        )

    def _html_document(
        self,
        entries: list[HtmlFontEntry],
        title: str,
        intro: str,
        sample_text: str,
    ) -> str:
        font_faces: list[str] = []
        sections: list[str] = []

        for index, entry in enumerate(entries):
            family_escaped = html.escape(entry.family)
            style_escaped = html.escape(entry.style)
            fullname_escaped = html.escape(entry.fullname)
            package_escaped = html.escape(entry.package)
            file_escaped = html.escape(entry.filename)
            font_url = html.escape(entry.relative_font_path)
            sample = html.escape(sample_text)
            css_family = f"fontgallery-{index}"
            font_faces.append(
                f"""
@font-face {{
  font-family: '{css_family}';
  src: url('{font_url}');
}}
"""
            )
            sections.append(
                f"""
<section class="specimen">
  <div class="meta">
    <h2>{family_escaped}</h2>
    <p><strong>Full name:</strong> {fullname_escaped}</p>
    <p><strong>Style:</strong> {style_escaped}</p>
    <p><strong>Package:</strong> {package_escaped}</p>
    <p><strong>File:</strong> {file_escaped}</p>
  </div>
  <div class="sample" style="font-family: '{css_family}', serif;">{sample}</div>
</section>
"""
            )

        style_block = "\n".join(font_faces)
        body_block = "\n".join(sections)
        return f"""<!DOCTYPE html>
<html lang="{html.escape(self.workspace.language)}">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    @page {{
      size: A4;
      margin: 1.2cm;
    }}
    body {{
      font-family: Liberation Sans, Arial, sans-serif;
      color: #111;
      line-height: 1.3;
    }}
    h1 {{
      font-size: 20pt;
      margin: 0 0 0.3cm 0;
    }}
    .intro {{
      font-size: 10pt;
      margin-bottom: 0.8cm;
    }}
    .specimen {{
      page-break-inside: avoid;
      break-inside: avoid;
      border-bottom: 1px solid #ccc;
      padding: 0 0 0.6cm 0;
      margin: 0 0 0.7cm 0;
    }}
    .meta h2 {{
      font-size: 15pt;
      margin: 0 0 0.15cm 0;
    }}
    .meta p {{
      margin: 0.03cm 0;
      font-size: 9.5pt;
    }}
    .sample {{
      margin-top: 0.35cm;
      white-space: pre-line;
      font-size: 13pt;
    }}
    {style_block}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="intro">{html.escape(intro)}</p>
  {body_block}
</body>
</html>
"""

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
