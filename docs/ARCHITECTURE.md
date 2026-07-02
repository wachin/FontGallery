# FontGallery Architecture

## Purpose

This document describes the current architecture of `FontGallery`, the responsibilities of each module, and the intended direction for future development.

## High-level design

`FontGallery` is being built as a desktop application in `PyQt6` for GNU/Linux. Its purpose is to help users build visual font collections from `.deb` packages, with a workflow centered on:

1. preparing a workspace;
2. extracting fonts into a master collection;
3. analyzing the extracted fonts;
4. deriving specialized sub-collections;
5. generating visual outputs such as HTML, image cards, and PDFs.

The architecture is intentionally split between:

- GUI orchestration;
- filesystem and workspace management;
- extraction logic;
- font analysis logic;
- output generation services.

## Current module layout

### Entry layer

- `main.py`
- `fontgallery/app.py`

Responsibilities:

- create the `QApplication`;
- resolve the working directory as project root;
- initialize shared services;
- start the main window.

### GUI layer

- `fontgallery/main_window.py`

Responsibilities:

- display the application interface;
- expose the main workflow buttons;
- present workspace state to the user;
- show operational logs;
- call services and present success or error dialogs.

Current design rule:

- the GUI should orchestrate work, not own business logic.

## Service layer

### Workspace service

- `fontgallery/services/workspace.py`

Responsibilities:

- define the managed folder structure;
- expose canonical project paths;
- create missing base directories;
- report basic directory status.

Current managed roots:

- `paquetes-deb`
- `album-fuentes`
- `album-fuentes-espanol`
- `album-fuentes-tecnicas`

Derived paths already modeled:

- `album-fuentes/fuentes-extraidas`
- `album-fuentes-espanol/fuentes-extraidas`
- `album-fuentes-tecnicas/fuentes-extraidas`

Future expansion:

- card directories;
- PDF output paths;
- stronger write-permission validation.

HTML output paths are now modeled in the workspace service.

### Extraction service

- `fontgallery/services/extraction.py`

Responsibilities:

- discover `.deb` packages;
- identify likely font packages;
- extract package contents with `dpkg-deb -x`;
- locate actual font files;
- avoid duplicates using `SHA256`;
- copy unique fonts into the master collection;
- read minimal metadata with `fc-scan`;
- skip broken or unreadable fonts.

Primary output:

- files copied into `album-fuentes/fuentes-extraidas/<package>/`
- in-memory extraction summary
- in-memory extracted font records

Architectural notes:

- this service is intentionally file-oriented;
- it does not generate HTML, cards, or PDFs;
- it does not classify fonts beyond package-level detection.

### Analysis service

- `fontgallery/services/analysis.py`

Responsibilities:

- scan extracted fonts from the master collection;
- read metadata and character coverage using `fc-scan`;
- determine whether a font supports Spanish;
- classify technical fonts using heuristics;
- derive specialized extracted subsets for later visual generation.

Primary outputs:

- files copied into `album-fuentes-espanol/fuentes-extraidas`
- files copied into `album-fuentes-tecnicas/fuentes-extraidas`
- in-memory analysis summary
- in-memory analyzed font records

Architectural notes:

- this service works from the extracted master collection rather than re-reading `.deb` packages;
- this separation makes future derived collections cheaper and easier to maintain;
- technical-font detection is currently heuristic and should remain configurable in the future.

### HTML generation service

- `fontgallery/services/html_generation.py`

Responsibilities:

- generate HTML indexes for the main, Spanish, and technical albums;
- embed local extracted font files with `@font-face`;
- exclude technical fonts from the main album;
- generate a technical-font exclusion report for the main album;
- produce print-friendly output intended for browser viewing and manual PDF printing.

Primary outputs:

- `album-fuentes/album-fuentes.html`
- `album-fuentes-espanol/album-fuentes-espanol.html`
- `album-fuentes-tecnicas/album-fuentes-tecnicas.html`

Architectural notes:

- this service works from extracted directories, not from `.deb` packages;
- it reuses the same classification direction established by the analysis stage;
- it is the first output-generation service integrated into the GUI.

## Data flow

The current data flow is:

1. User places `.deb` packages in `paquetes-deb`.
2. `WorkspaceService` prepares the required folders.
3. `ExtractionService` extracts all unique fonts to `album-fuentes/fuentes-extraidas`.
4. `AnalysisService` scans the master collection.
5. `AnalysisService` derives:
   - Spanish-capable non-technical fonts;
   - technical fonts.
6. `HtmlGenerationService` renders the HTML albums from those extracted directories.

This establishes `album-fuentes` as the source of truth for later album generation.

## Design principles

### Master collection first

The architecture is built around a single master extracted collection:

- extract once from `.deb`;
- analyze once from extracted files;
- derive many subsets without repeating extraction.

This reduces repeated I/O and avoids duplicating package-level work.

### Service-first business logic

Operational logic should live in services rather than in the GUI. This makes the project easier to:

- test;
- refactor;
- automate;
- reuse from CLI tools later if needed.

### Folder-based outputs

Every processing stage should leave inspectable files on disk. This is useful because:

- users can inspect results without the app;
- developers can debug intermediate artifacts;
- later stages can reuse earlier outputs.

## External system dependencies

The current architecture already depends on:

- `PyQt6`
- `dpkg-deb`
- `fc-scan`

Likely future dependencies:

- `Pillow` for image cards;
- browser or renderer integration only if needed for HTML-to-PDF workflows.

### Card generation service

Proposed file:

- `fontgallery/services/card_generation.py`

Responsibilities:

- render per-font cards as PNG images;
- provide deterministic file output for PDF composition;
- act as an alternative to HTML-based rendering.

### PDF generation service

Proposed file:

- `fontgallery/services/pdf_generation.py`

Responsibilities:

- build PDFs from cards or another stable rendering pipeline;
- avoid overlap issues seen in naive direct PDF text composition;
- support designer-friendly exports.

## Current architectural risks

- long-running operations still execute on the GUI thread;
- write checks are still shallow;
- technical classification may need richer rules and documentation;
- there is not yet a persistent metadata cache.

## Recommended near-term direction

The next architectural step should be:

1. introduce a card generation service;
2. define a reusable font record format shared by extraction, analysis, and HTML generation;
3. keep the GUI limited to starting jobs and showing results;
4. prepare later threading or worker infrastructure once output generation is integrated.
