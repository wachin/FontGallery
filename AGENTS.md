# AGENTS.md

## Repository scope

This repository contains `FontGallery`, a `PyQt6` desktop application for GNU/Linux focused on building visual font albums from `.deb` packages.

## Working directory

- Always start Codex sessions from the repository root.
- Do not assume subdirectory execution.
- Many paths in the project currently depend on `Path.cwd()`.

## Main commands

### Run the application

```bash
python3 main.py
```

### Run tests

```bash
env QT_QPA_PLATFORM=offscreen pytest -q
```

### Rebuild translations

```bash
./translations/update_translations.sh
```

## Runtime and development dependencies

For Debian 12 / MX Linux 23, install at least:

```bash
sudo apt install \
  python3-pyqt6 \
  python3-pytest \
  pyqt6-dev-tools \
  qtchooser \
  fontconfig \
  dpkg
```

Relevant system tools used by the project:

- `dpkg-deb`
- `fc-scan`
- `pylupdate6`
- `lrelease`

## Language and translation rules

- English is the source language of the codebase and the UI.
- UI strings should remain translation-ready with `self.tr(...)` in Qt widgets.
- Service-layer strings that must be translated should use `QCoreApplication.translate(...)`.
- Translation files live in `translations/`.
- Spanish translation support already exists and must be preserved.

## Workspace naming behavior

- The application detects the system locale at startup.
- In a new empty workspace, it creates folder names in English or Spanish depending on the locale.
- If an older workspace already exists, the application must reuse it instead of mixing localized folder names.
- Do not break compatibility with existing Spanish folder structures.

## Existing project structure

Important directories and files:

- `fontgallery/`
- `tests/`
- `translations/`
- `docs/`
- `ROADMAP.md`
- `README.md`

## Testing expectations

- If you modify workspace behavior, update or add tests in `tests/test_workspace.py`.
- If you modify translations or translatable strings, update the `.ts` files and recompile `.qm`.
- If you modify UI text or service text, verify that translation extraction still works.

## Current implementation status

Already implemented:

- localized workspace naming for English and Spanish;
- extraction of fonts from `.deb` packages;
- analysis of the master collection;
- derivation of Spanish and technical albums;
- HTML album generation;
- Qt translation loading;
- initial pytest coverage for workspace and translation behavior.

Not yet implemented:

- PNG card generation;
- PDF generation from the GUI;
- background workers/threads for long-running tasks;
- deeper designer-oriented font filters.

## Documentation discipline

- Keep `README.md`, `ROADMAP.md`, and `docs/` aligned with actual implementation status.
- When adding dependencies, document both Python-level and Debian/MX Linux package-level requirements.
