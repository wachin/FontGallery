from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from fontgallery.services.card_generation import CardGenerationService
from fontgallery.services.workspace import WorkspaceService


def _find_test_font() -> Path:
    for root in (Path("/usr/share/fonts"), Path("/usr/local/share/fonts")):
        if not root.exists():
            continue
        for candidate in root.rglob("DejaVuSans.ttf"):
            if candidate.is_file():
                return candidate
    raise FileNotFoundError("No DejaVuSans.ttf font was found for card-generation tests")


def test_card_generation_creates_png_cards_for_all_albums(tmp_path: Path) -> None:
    try:
        font_path = _find_test_font()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))

    workspace = WorkspaceService(tmp_path, language_code="es_ES")
    workspace.prepare_structure()

    main_regular = workspace.album_main_extract_dir / "fonts-demo" / "fonts-demo__DejaVuSans.ttf"
    main_technical = workspace.album_main_extract_dir / "latex-demo" / "latex-demo__cmex-demo.ttf"
    spanish_font = workspace.album_es_extract_dir / "fonts-demo" / "fonts-demo__DejaVuSans.ttf"
    technical_font = workspace.album_tech_extract_dir / "latex-demo" / "latex-demo__cmex-demo.ttf"

    for target in (main_regular, main_technical, spanish_font, technical_font):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(font_path, target)

    service = CardGenerationService(workspace)

    summaries = service.generate_all_albums()
    summaries_by_label = {summary.label: summary for summary in summaries}

    assert summaries_by_label["main"].generated_cards == 1
    assert summaries_by_label["main"].excluded_fonts == 1
    assert summaries_by_label["main"].render_errors == 0
    assert summaries_by_label["spanish"].generated_cards == 1
    assert summaries_by_label["technical"].generated_cards == 1

    assert (workspace.album_main_cards_dir / "fonts-demo" / "fonts-demo__DejaVuSans.png").is_file()
    assert (workspace.album_es_cards_dir / "fonts-demo" / "fonts-demo__DejaVuSans.png").is_file()
    assert (workspace.album_tech_cards_dir / "latex-demo" / "latex-demo__cmex-demo.png").is_file()


def test_card_generation_reports_progress(tmp_path: Path) -> None:
    try:
        font_path = _find_test_font()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))

    workspace = WorkspaceService(tmp_path, language_code="es_ES")
    workspace.prepare_structure()

    for target in (
        workspace.album_main_extract_dir / "fonts-demo" / "fonts-demo__DejaVuSans.ttf",
        workspace.album_es_extract_dir / "fonts-demo" / "fonts-demo__DejaVuSans.ttf",
        workspace.album_tech_extract_dir / "latex-demo" / "latex-demo__cmex-demo.ttf",
    ):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(font_path, target)

    progress_updates: list[tuple[int, int, str]] = []
    service = CardGenerationService(workspace)

    service.generate_all_albums(
        progress=lambda current, total, label: progress_updates.append((current, total, label))
    )

    assert progress_updates
    assert progress_updates[0][0] == 0
    assert progress_updates[-1][0] == progress_updates[-1][1]


def test_card_generation_wraps_sample_lines_to_card_width(tmp_path: Path) -> None:
    try:
        font_path = _find_test_font()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))

    workspace = WorkspaceService(tmp_path, language_code="es_ES")
    service = CardGenerationService(workspace)
    image_module, image_draw_module, image_font_module = service._require_pillow()
    image = image_module.new("RGB", (1600, 1000), "#ffffff")
    draw = image_draw_module.Draw(image)
    sample_font = image_font_module.truetype(str(font_path), size=56)

    wrapped_lines = service._wrap_sample_lines(
        draw=draw,
        text=(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "0123456789 áéíóú üñ |@#~½{[]}¡!\"'$%&\\ /()=¿?<> +-ºª÷©°®\n"
            "\"Nunca se aparten de ti la misericordia y la verdad; átalas a tu cuello.\""
        ),
        font=sample_font,
        max_width=1420,
    )

    assert len(wrapped_lines) > 3
    assert all(service._text_width(draw, line, sample_font) <= 1420 for line in wrapped_lines if line)
