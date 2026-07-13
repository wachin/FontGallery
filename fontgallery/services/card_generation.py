from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import QCoreApplication

from .analysis import TECHNICAL_KEYWORDS
from .html_generation import DEFAULT_SAMPLE_TEXT, TECHNICAL_SAMPLE_TEXT
from .workspace import WorkspaceService

FONT_SUFFIXES = {".ttf", ".otf", ".ttc", ".pfa", ".pfb"}


@dataclass(frozen=True)
class CardFontEntry:
    family: str
    style: str
    fullname: str
    package: str
    filename: str
    path: Path


@dataclass(frozen=True)
class CardAlbumSummary:
    label: str
    output_dir: Path
    generated_cards: int
    excluded_fonts: int
    render_errors: int


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


class CardGenerationService:
    def __init__(self, workspace: WorkspaceService) -> None:
        self.workspace = workspace

    def generate_all_albums(
        self,
        log: Callable[[str], None] | None = None,
    ) -> list[CardAlbumSummary]:
        def emit(message: str) -> None:
            if log is not None:
                log(message)

        self.workspace.prepare_structure()
        self._require_pillow()

        return [
            self._generate_album(
                label="main",
                source_dir=self.workspace.album_main_extract_dir,
                output_dir=self.workspace.album_main_cards_dir,
                sample_text=DEFAULT_SAMPLE_TEXT,
                include_technical=False,
                emit=emit,
            ),
            self._generate_album(
                label="spanish",
                source_dir=self.workspace.album_es_extract_dir,
                output_dir=self.workspace.album_es_cards_dir,
                sample_text=DEFAULT_SAMPLE_TEXT,
                include_technical=True,
                emit=emit,
            ),
            self._generate_album(
                label="technical",
                source_dir=self.workspace.album_tech_extract_dir,
                output_dir=self.workspace.album_tech_cards_dir,
                sample_text=TECHNICAL_SAMPLE_TEXT,
                include_technical=True,
                emit=emit,
            ),
        ]

    def _generate_album(
        self,
        label: str,
        source_dir: Path,
        output_dir: Path,
        sample_text: str,
        include_technical: bool,
        emit: Callable[[str], None],
    ) -> CardAlbumSummary:
        entries, excluded_fonts = self._collect_entries(
            source_dir=source_dir,
            include_technical=include_technical,
        )

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        render_errors = 0
        generated_cards = 0

        for entry in entries:
            package_dir = output_dir / entry.package
            package_dir.mkdir(parents=True, exist_ok=True)
            card_path = package_dir / f"{entry.path.stem}.png"
            try:
                self._render_card(entry, sample_text, card_path)
            except Exception as exc:
                render_errors += 1
                emit(
                    QCoreApplication.translate(
                        "CardGenerationService",
                        "Skipped card for {font} due to rendering error: {error}",
                    ).format(font=entry.filename, error=exc)
                )
                continue
            generated_cards += 1

        emit(
            QCoreApplication.translate(
                "CardGenerationService",
                "Generated {count} PNG cards for the {label} album in {path}",
            ).format(count=generated_cards, label=label, path=output_dir)
        )
        return CardAlbumSummary(
            label=label,
            output_dir=output_dir,
            generated_cards=generated_cards,
            excluded_fonts=excluded_fonts,
            render_errors=render_errors,
        )

    def _collect_entries(
        self,
        source_dir: Path,
        include_technical: bool,
    ) -> tuple[list[CardFontEntry], int]:
        if not source_dir.exists():
            raise FileNotFoundError(
                QCoreApplication.translate(
                    "CardGenerationService",
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
                    "CardGenerationService",
                    "No extracted fonts were found in: {path}",
                ).format(path=source_dir)
            )

        entries: list[CardFontEntry] = []
        excluded_fonts = 0
        for font_path in font_paths:
            family, style, fullname = scan_font(font_path)
            package = font_path.parent.name
            if not include_technical and self._is_technical_font(
                package=package,
                family=family,
                style=style,
                fullname=fullname,
                filename=font_path.name,
            ):
                excluded_fonts += 1
                continue

            entries.append(
                CardFontEntry(
                    family=family,
                    style=style,
                    fullname=fullname,
                    package=package,
                    filename=font_path.name,
                    path=font_path,
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
        return entries, excluded_fonts

    def _render_card(self, entry: CardFontEntry, sample_text: str, output_path: Path) -> None:
        image_module, image_draw_module, image_font_module = self._require_pillow()

        image = image_module.new("RGB", (1600, 1000), "#f7f1e8")
        draw = image_draw_module.Draw(image)

        heading_font = self._load_ui_font(image_font_module, size=36)
        meta_font = self._load_ui_font(image_font_module, size=24)
        footer_font = self._load_ui_font(image_font_module, size=20)
        sample_lines, sample_font, sample_spacing = self._fit_sample_text(
            draw=draw,
            image_font_module=image_font_module,
            font_path=entry.path,
            sample_text=sample_text,
            max_width=1420,
            max_height=560,
        )

        draw.rounded_rectangle((40, 40, 1560, 960), radius=28, fill="#fffdf9", outline="#d8ccb7", width=3)
        draw.text((90, 90), entry.family, fill="#1b1b1b", font=heading_font)
        meta_text = (
            f"{entry.fullname}\n"
            f"Style: {entry.style}\n"
            f"Package: {entry.package}\n"
            f"File: {entry.filename}"
        )
        draw.text(
            (90, 135),
            meta_text,
            fill="#4a4035",
            font=meta_font,
            spacing=8,
        )
        draw.line((90, 250, 1510, 250), fill="#d8ccb7", width=2)
        draw.multiline_text(
            (90, 300),
            "\n".join(sample_lines),
            fill="#111111",
            font=sample_font,
            spacing=sample_spacing,
        )
        draw.text(
            (90, 900),
            QCoreApplication.translate(
                "CardGenerationService",
                "Generated by FontGallery from locally extracted fonts.",
            ),
            fill="#6b6259",
            font=footer_font,
        )
        image.save(output_path, format="PNG")

    def _require_pillow(self):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as exc:
            raise RuntimeError(
                QCoreApplication.translate(
                    "CardGenerationService",
                    "Pillow is required for PNG card generation. Install the Python package 'Pillow' or the Debian package 'python3-pil'.",
                )
            ) from exc
        return Image, ImageDraw, ImageFont

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

    @lru_cache(maxsize=1)
    def _ui_font_path(self) -> str | None:
        for pattern in ("DejaVu Sans", "Noto Sans", "Liberation Sans", "sans-serif"):
            try:
                result = run(
                    ["fc-match", "--format", "%{file}\n", pattern],
                    capture_output=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
            path = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
            if path:
                return path
        return None

    def _load_ui_font(self, image_font_module, size: int):
        font_path = self._ui_font_path()
        if font_path:
            try:
                return image_font_module.truetype(font_path, size=size)
            except OSError:
                pass
        return image_font_module.load_default()

    def _fit_sample_text(
        self,
        draw,
        image_font_module,
        font_path: Path,
        sample_text: str,
        max_width: int,
        max_height: int,
    ):
        for size in range(56, 21, -2):
            sample_font = image_font_module.truetype(str(font_path), size=size)
            spacing = max(10, size // 3)
            wrapped_lines = self._wrap_sample_lines(
                draw=draw,
                text=sample_text,
                font=sample_font,
                max_width=max_width,
            )
            bbox = draw.multiline_textbbox((0, 0), "\n".join(wrapped_lines), font=sample_font, spacing=spacing)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width <= max_width and height <= max_height:
                return wrapped_lines, sample_font, spacing

        sample_font = image_font_module.truetype(str(font_path), size=20)
        spacing = 10
        wrapped_lines = self._wrap_sample_lines(
            draw=draw,
            text=sample_text,
            font=sample_font,
            max_width=max_width,
        )
        return wrapped_lines, sample_font, spacing

    def _wrap_sample_lines(
        self,
        draw,
        text: str,
        font,
        max_width: int,
    ) -> list[str]:
        wrapped_lines: list[str] = []
        for raw_line in text.splitlines():
            wrapped_lines.extend(self._wrap_single_line(draw, raw_line, font, max_width))
        return wrapped_lines

    def _wrap_single_line(
        self,
        draw,
        text: str,
        font,
        max_width: int,
    ) -> list[str]:
        if not text:
            return [""]

        if self._text_width(draw, text, font) <= max_width:
            return [text]

        break_chars = {" ", "|", "/", "\\", "-", "+", "=", "<", ">", "(", ")", "[", "]", "{", "}", ",", ";"}
        lines: list[str] = []
        current = ""
        last_break_index = -1

        for char in text:
            candidate = current + char
            if self._text_width(draw, candidate, font) <= max_width:
                current = candidate
                if char in break_chars:
                    last_break_index = len(current)
                continue

            if current:
                if last_break_index > 0:
                    lines.append(current[:last_break_index].rstrip())
                    remainder = current[last_break_index:].lstrip()
                    current = remainder + char
                else:
                    lines.append(current.rstrip())
                    current = char
            else:
                lines.append(char)
                current = ""

            last_break_index = -1
            for index, existing_char in enumerate(current, start=1):
                if existing_char in break_chars:
                    last_break_index = index

        if current:
            lines.append(current.rstrip())
        return lines

    def _text_width(self, draw, text: str, font) -> int:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
