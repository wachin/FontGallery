# FontGallery

FontGallery is a PyQt6 desktop application for GNU/Linux that builds visual font albums from `.deb` packages.

## System dependencies

For Debian 12 / MX Linux 23, install at least:

```bash
sudo apt install \
  python3-pyqt6 \
  python3-pil \
  python3-pytest \
  pyqt6-dev-tools \
  qtchooser \
  fontconfig \
  dpkg
```

What each package is used for:

- `python3-pyqt6`: runtime GUI bindings.
- `python3-pil`: Pillow runtime used for PNG card generation.
- `python3-pytest`: test runner for the `tests/` directory.
- `pyqt6-dev-tools`: provides `pylupdate6` for updating `.ts` translation sources.
- `qtchooser`: provides `lrelease` in this Debian 12 / MX Linux 23 environment.
- `fontconfig`: provides `fc-scan` for font metadata and charset analysis.
- `dpkg`: provides `dpkg-deb` for extracting `.deb` packages.

Relevant package lists available in this repository:

- `packages_available_debian12_pyqt6.txt`
- `packages_available_debian12_python3.txt`

## Python dependencies

The current Python dependency file is:

```bash
pip install -r requirements.txt
```

At the moment it contains:

- `PyQt6`
- `Pillow`

On Debian-based systems, the recommended installation method for this project is the `apt` packages listed above.

## Run

```bash
python3 main.py
```

## Tests

Tests live in `tests/`.

Run them with:

```bash
env QT_QPA_PLATFORM=offscreen pytest -q
```

The current tests cover:

- workspace folder naming for English and Spanish;
- creation of the derived extracted-font folders;
- creation of the derived PNG card folders;
- workspace write-access validation;
- reuse of an existing localized workspace;
- PNG card generation from extracted fonts;
- loading of Qt translations;
- translation of UI and service strings.

## Translations

Translation files live in `translations/`.

Update `.ts` and `.qm` files with:

```bash
./translations/update_translations.sh
```

This uses:

- `pylupdate6`
- `lrelease`
