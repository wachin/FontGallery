# HTML Generation Plan

## Purpose

This document defines the planned approach for generating the HTML font albums inside `FontGallery`.

The goal is to move the existing standalone script behavior into reusable services integrated with the GUI, without losing the visual quality already achieved in browser-based rendering.

## Why HTML matters in this project

HTML is currently the most reliable visual output format for this workflow because:

- browsers render many fonts more cleanly than direct PDF text composition;
- the user already validated that printing the generated HTML with Google Chrome produces better PDFs;
- HTML can serve both as an interactive preview and as an intermediate format for PDF export.

Because of that, HTML generation should be treated as a first-class output stage, not just a temporary artifact.

## Albums to generate

The application should generate three HTML indexes:

- `album-fuentes/album-fuentes.html`
- `album-fuentes-espanol/album-fuentes-espanol.html`
- `album-fuentes-tecnicas/album-fuentes-tecnicas.html`

Each HTML file should reflect the fonts located in its corresponding `fuentes-extraidas` directory.

## Scope of the first HTML implementation

The first integrated implementation should focus on:

- generating static HTML files;
- embedding per-font previews with `@font-face`;
- listing fonts in a stable, readable order;
- keeping output suitable for browser viewing and print-to-PDF;
- reusing the same sample texts already proven useful in the current workflow.

The first version does not need to include:

- advanced search or filtering in the browser;
- JavaScript-heavy UI behavior;
- card-image rendering;
- PDF export from inside the application.

## Proposed service

Proposed module:

- `fontgallery/services/html_generation.py`

Suggested responsibilities:

- scan an extracted album directory;
- read or receive analyzed font records;
- generate the target HTML file;
- write supporting CSS if external styling is preferred;
- optionally create a summary report for excluded fonts.

## Inputs

The HTML generation service should work from these inputs:

- the album root directory;
- the extracted-font directory for that album;
- optional analysis metadata;
- optional filtering rules depending on album type.

Practical inputs by album:

- main album: all non-technical fonts intended for general design use;
- Spanish album: only fonts supporting Spanish and not marked technical;
- technical album: fonts classified as technical.

## Output structure

The initial plan is to generate self-contained HTML files at:

- `album-fuentes/album-fuentes.html`
- `album-fuentes-espanol/album-fuentes-espanol.html`
- `album-fuentes-tecnicas/album-fuentes-tecnicas.html`

Optional future support files:

- `styles.css`
- report files in Markdown or plain text

The preferred initial approach is a single-file HTML output whenever practical, because it is easier for users to move, open, print, and archive.

## Visual structure of each font entry

Each font block should include:

- family name;
- full font name;
- style;
- package name;
- source file name;
- sample lowercase text;
- sample uppercase text;
- sample numbers and punctuation;
- Spanish sample line;
- optional Bible verse or longer paragraph already used in the existing project.

The output should prioritize readability and print stability over compactness.

## Ordering rules

The first implementation should keep a deterministic order:

1. family name
2. full name
3. style
4. file name

This should match the ordering already used by the extraction and analysis services where possible.

## Rendering strategy

The preferred rendering strategy is:

1. define one `@font-face` block per extracted font file;
2. assign a unique CSS class to each preview block;
3. render preview text using the actual local extracted file;
4. keep layout simple and print-friendly.

This avoids requiring system-wide font installation for preview generation.

## Print-oriented constraints

Since the user already confirmed browser printing works better than direct PDF composition, the HTML should be designed for print stability:

- avoid dynamic layout tricks;
- avoid overlapping text blocks;
- use predictable margins and spacing;
- avoid squeezing too many font samples into one printed page;
- keep CSS compatible with Chromium-based printing.

## Fonts that should not appear in the main design album

The HTML generator should preserve the project classification rules:

- technical and math-oriented fonts should not appear in `album-fuentes.html`;
- they should instead be routed to `album-fuentes-tecnicas.html`;
- Spanish-only filtering should remain separate from technical classification.

This is important because many technical fonts are not suitable for general graphic design browsing.

## Reuse of previous work

The implementation should reuse ideas and logic from the older scripts, especially:

- `generar_album_fuentes.py`
- `generar_album_fuentes_espanol.py`
- `generar_album_fuentes_tecnicas.py`

However, the code should be refactored into reusable Python functions or classes rather than copied as large script bodies into the GUI.

## Suggested implementation steps

### Step 1

Create `html_generation.py` with:

- a small service class;
- a record-to-HTML rendering method;
- an album-level generation method.

### Step 2

Implement generation for only one album first:

- `album-fuentes/album-fuentes.html`

This reduces complexity while validating the service design.

### Step 3

Extend the same service to:

- `album-fuentes-espanol/album-fuentes-espanol.html`
- `album-fuentes-tecnicas/album-fuentes-tecnicas.html`

### Step 4

Connect the service to the GUI with a new button:

- `Generar indices HTML`

### Step 5

Add report output for:

- excluded technical fonts from the main album;
- fonts skipped due to missing metadata or broken files.

## Risks and open questions

- some extracted fonts may still render poorly in browsers because of the font itself, not because of missing dependencies;
- technical fonts may require special exclusion handling;
- very large HTML files may become slower to open;
- there is not yet a shared metadata cache between analysis and HTML generation.

## Recommended next implementation target

The next implementation target should be a minimal but complete HTML generation service for the main album, with:

- deterministic ordering;
- embedded `@font-face` declarations;
- print-friendly CSS;
- browser-ready output for manual PDF printing.
