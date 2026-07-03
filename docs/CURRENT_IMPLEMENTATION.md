# Current FontGallery Implementation

## Goal of this stage

At this stage, the base `FontGallery` application flow has been implemented to:

- prepare the project folder structure;
- extract fonts from `.deb` packages into a master collection;
- analyze the master collection;
- derive subsets for Spanish-capable fonts and technical fonts.
- generate HTML albums for the main, Spanish, and technical collections.

## Current project structure

### Entry point

- `main.py`
- `fontgallery/app.py`

The application starts from the current working directory and uses that directory as the project root.

### Main window

- `fontgallery/main_window.py`

The main window already includes these buttons:

- `Preparar estructura`
- `Extraer todas las fuentes a album-fuentes`
- `Analizar y clasificar colección maestra`
- `Generar indices HTML`
- `Actualizar estado`

It also shows:

- the base working directory;
- the number of detected `.deb` packages;
- the status of managed folders;
- a built-in log output panel.

### Services

- `fontgallery/services/workspace.py`
- `fontgallery/services/extraction.py`
- `fontgallery/services/analysis.py`
- `fontgallery/services/html_generation.py`

### Translation assets

- `translations/fontgallery_en.ts`
- `translations/fontgallery_es.ts`
- `translations/fontgallery_en.qm`
- `translations/fontgallery_es.qm`

## Implemented flow

### 1. Prepare structure

`WorkspaceService` creates or verifies these base folders:

- `paquetes-deb`
- `album-fuentes`
- `album-fuentes-espanol`
- `album-fuentes-tecnicas`

It also exposes derived paths used by the services:

- `album-fuentes/fuentes-extraidas`
- `album-fuentes-espanol/fuentes-extraidas`
- `album-fuentes-tecnicas/fuentes-extraidas`

The prepare step now also creates those derived extracted-font folders up front and validates write access before attempting to create missing directories.

### 2. Extract fonts from `.deb` packages

`ExtractionService` implements extraction into the master collection:

- reads `.deb` files inside `paquetes-deb`;
- filters packages that appear to be font packages;
- extracts them with `dpkg-deb -x` into a temporary directory;
- locates font files such as `.ttf`, `.otf`, `.ttc`, `.pfa`, and `.pfb`;
- avoids duplicates by `SHA256` hash;
- copies unique fonts into `album-fuentes/fuentes-extraidas/<package>/`;
- reads basic metadata with `fc-scan`;
- skips broken fonts or fonts that cannot be analyzed.

The metadata currently stored in memory is:

- family;
- style;
- full name;
- package;
- file name;
- path.

### 3. Analyze the master collection

`AnalysisService` works from `album-fuentes/fuentes-extraidas` and does not read the `.deb` packages again.

It currently does the following:

- scans all extracted fonts;
- reads metadata again with `fc-scan`;
- analyzes `charset` to detect Unicode coverage;
- checks Spanish support using these characters:
  - `áéíóúüñÁÉÍÓÚÜÑ`
- classifies technical fonts using heuristics based on family name, file name, and package name.

Current technical keywords include:

- `jsmath`
- `latex`
- `tex`
- `lyx`
- `math`
- `symbol`
- `rsfs`
- `msam`
- `msbm`
- `cmex`
- `cmsy`
- `cmmi`
- and other related terms

### 4. Derive sub-albums

After the analysis step, the service creates these subsets:

- `album-fuentes-espanol/fuentes-extraidas`
- `album-fuentes-tecnicas/fuentes-extraidas`

Current rules:

- `album-fuentes-espanol` receives fonts with Spanish support that are not technical;
- `album-fuentes-tecnicas` receives fonts classified as technical.

### 5. Generate HTML albums

`HtmlGenerationService` generates these files:

- `album-fuentes/album-fuentes.html`
- `album-fuentes-espanol/album-fuentes-espanol.html`
- `album-fuentes-tecnicas/album-fuentes-tecnicas.html`

Current behavior:

- defines one `@font-face` rule per extracted font;
- renders stable specimen blocks for each font;
- uses a general sample text for the main and Spanish albums;
- uses a technical sample text for the technical album;
- excludes technical fonts from the main album;
- writes an exclusion report for technical fonts removed from the main album.

### 6. Load translations

The application now uses English as its source UI language and prepares interface strings with `self.tr(...)` in the main window.

At startup:

- the system locale is detected with `QLocale.system().name()`;
- the workspace naming scheme is resolved from that locale;
- the application attempts to load a matching `.qm` file from `translations/`.

At the moment, the supported UI languages are:

- English
- Spanish

## Current ROADMAP status

These blocks are already implemented:

- `PyQt6` application skeleton;
- minimal main window;
- structure preparation;
- full extraction into `album-fuentes`;
- duplicate detection and extraction error handling;
- master collection analysis;
- derivation into Spanish and technical albums.
- HTML generation for all three albums from the GUI.

## External dependencies used by the current code

In addition to `PyQt6`, the current flow depends on these system tools:

- `dpkg-deb`
- `fc-scan`

Without these tools, extraction and analysis will not work.

### Debian 12 / MX Linux 23 packages

For development and testing, the current recommended package set is:

```bash
sudo apt install \
  python3-pyqt6 \
  python3-pytest \
  pyqt6-dev-tools \
  qtchooser \
  fontconfig \
  dpkg
```

Purpose of each package:

- `python3-pyqt6`: GUI runtime and Qt Python bindings.
- `python3-pytest`: test runner for the local test suite.
- `pyqt6-dev-tools`: provides `pylupdate6` for translation source updates.
- `qtchooser`: provides `lrelease` in this environment for `.qm` generation.
- `fontconfig`: provides `fc-scan`.
- `dpkg`: provides `dpkg-deb`.

Repository reference files available for package review:

- `packages_available_debian12_pyqt6.txt`
- `packages_available_debian12_python3.txt`

## Current limitations

- PNG card generation is not implemented in the GUI yet;
- PDF generation is not implemented in the GUI yet;
- HTML generation currently depends on the extracted directories already being present;
- technical font detection is still heuristic-based;
- additional designer-oriented filters such as monospaced, serif, or display are not implemented yet;
- the interface still runs everything on the main thread, so large jobs may freeze the window.

## How to test the implemented features

### Automated tests

The project now includes a `tests/` directory.

Run the tests with:

```bash
pytest
```

Current coverage includes:

- workspace naming in English and Spanish;
- reuse of an existing localized workspace;
- loading of Qt translations;
- translation of UI and service strings.

### Run the application

```bash
python3 main.py
```

### Recommended test flow

1. Put `.deb` packages into `paquetes-deb`.
2. Click `Preparar estructura`.
3. Click `Extraer todas las fuentes a album-fuentes`.
4. Click `Analizar y clasificar colección maestra`.
5. Click `Generar indices HTML`.
6. Review the log panel and the generated folders.

## Recommended next step

The next most useful step is to add PNG card generation as a reusable service and connect it to the GUI, using the same album structure already produced by extraction, analysis, and HTML generation.
