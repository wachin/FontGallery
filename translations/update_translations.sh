#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

pylupdate6 \
  fontgallery/main_window.py \
  fontgallery/services/workspace.py \
  fontgallery/services/extraction.py \
  fontgallery/services/analysis.py \
  fontgallery/services/html_generation.py \
  fontgallery/services/card_generation.py \
  -ts translations/fontgallery_en.ts \
  -ts translations/fontgallery_es.ts
lrelease translations/fontgallery_en.ts translations/fontgallery_es.ts
