# ROADMAP

## Vision

- [x] Build a `PyQt6` application for GNU/Linux focused on **Graphic Design**.
- [ ] Help people who are new to Linux visually discover the fonts available in the repositories.
- [ ] Use the font collection gathered by Ubuntu Studio and other repository-downloaded fonts as a starting point.
- [ ] Clearly separate fonts useful for general graphic design from technical or mathematical fonts.

## Core principle

- [ ] Use `album-fuentes` as the **master collection**.
- [x] First extract all fonts from `paquetes-deb` into `album-fuentes/fuentes-extraidas`.
- [ ] Analyze that master collection only once.
- [ ] Derive other thematic albums from that master collection without extracting the `.deb` files again.

## Folder structure

### Base folders

- [x] Create `/paquetes-deb` if it does not exist.
- [x] Create `/album-fuentes` if it does not exist.
- [x] Create `/album-fuentes-espanol` if it does not exist.
- [x] Create `/album-fuentes-tecnicas` if it does not exist.

### Extracted font subfolders

- [x] Create `/album-fuentes/fuentes-extraidas` if it does not exist.
- [x] Create `/album-fuentes-espanol/fuentes-extraidas` if it does not exist.
- [x] Create `/album-fuentes-tecnicas/fuentes-extraidas` if it does not exist.

### Card subfolders

- [x] Create `/album-fuentes/tarjetas-fuentes` if it does not exist.
- [x] Create `/album-fuentes-espanol/tarjetas-fuentes-espanol` if it does not exist.
- [x] Create `/album-fuentes-tecnicas/tarjetas-fuentes-tecnicas` if it does not exist.

## Desired main workflow

### Step 1. Prepare the structure

- [x] Button to prepare the folder structure.
- [x] Verify write permissions.
- [x] Show clear messages if a folder cannot be created.

### Step 2. Extract all fonts into the master collection

- [x] Read `.deb` packages from `paquetes-deb`.
- [x] Detect which packages contain fonts.
- [x] Extract unique fonts into `album-fuentes/fuentes-extraidas`.
- [x] Avoid duplicates by hash.
- [x] Record fonts that cannot be opened or copied.

### Step 3. Analyze the master collection

- [x] Read metadata from all extracted fonts.
- [x] Obtain family, style, full name, and file name.
- [x] Detect Unicode coverage.
- [x] Detect whether the font properly supports Spanish.
- [x] Detect whether the font is technical or mathematical.
- [ ] Detect other categories useful for designers.

### Step 4. Derive sub-albums from `album-fuentes`

- [ ] Create `album-fuentes-espanol` from `album-fuentes`.
- [ ] Create `album-fuentes-tecnicas` from `album-fuentes`.
- [ ] Create exclusion and classification reports.

### Step 5. Generate HTML indexes

- [x] Create `album-fuentes/album-fuentes.html`.
- [x] Create `album-fuentes-espanol/album-fuentes-espanol.html`.
- [x] Create `album-fuentes-tecnicas/album-fuentes-tecnicas.html`.

### Step 6. Generate cards

- [x] Generate PNG cards for `album-fuentes`.
- [x] Generate PNG cards for `album-fuentes-espanol`.
- [x] Generate PNG cards for `album-fuentes-tecnicas`.

### Step 7. Generate PDFs

- [ ] Generate PDF for `album-fuentes`.
- [ ] Generate PDF for `album-fuentes-espanol`.
- [ ] Generate PDF for `album-fuentes-tecnicas`.

## Base albums of the project

### Main album

- [ ] Keep `album-fuentes` as the main catalog for general graphic design.
- [ ] Exclude technical or mathematical fonts from that album.
- [ ] Include all fonts that are visually useful for common composition.

### Spanish album

- [ ] Keep `album-fuentes-espanol` as a subset with proper support for `áéíóúüñÁÉÍÓÚÜÑ`.
- [ ] Also exclude technical fonts from that album.

### Technical album

- [ ] Keep `album-fuentes-tecnicas` as a separate album for mathematical, symbolic, or technical-composition fonts.
- [ ] Include fonts from `jsMath`, `LyX`, `LaTeX`, `TeX`, and similar ecosystems when applicable.

## Useful filters for designers

### Priority filters

- [ ] Fonts with Spanish support.
- [ ] Technical or mathematical fonts.
- [ ] Monospaced fonts.
- [ ] Serif fonts.
- [ ] Sans serif fonts.
- [ ] Script or calligraphic fonts.
- [ ] Display or decorative fonts.
- [ ] Handwritten fonts.
- [ ] Fonts with many variants.
- [ ] Fonts suitable for long text.
- [ ] Fonts suitable for titles.

### Possible technical filters

- [ ] Filter by family.
- [ ] Filter by style.
- [ ] Filter by Unicode coverage.
- [ ] Filter by glyph count.
- [ ] Filter by fixed width or proportional width.
- [ ] Filter by real bold presence.
- [ ] Filter by real italic presence.
- [ ] Filter by small caps if metadata makes it possible.
- [ ] Filter by OpenType features if they can be detected.
- [ ] Filter by variable font if it can be detected.

### Recommended future graphic-design filters

- [ ] `album-fuentes-monoespaciadas`
- [ ] `album-fuentes-serif`
- [ ] `album-fuentes-sans`
- [ ] `album-fuentes-display`
- [ ] `album-fuentes-script`
- [ ] `album-fuentes-con-muchas-variantes`
- [ ] `album-fuentes-latino-basicas`
- [ ] `album-fuentes-unicode-amplias`

## Classification criteria already defined

### General graphic design fonts

- [ ] Keep in the main album the fonts useful for posters, branding, publishing, layout, and general visual composition.

### Spanish fonts

- [ ] Keep in the Spanish album only fonts that truly cover the characters required by Spanish-speaking users.

### Technical fonts

- [ ] Keep technical or mathematical fonts out of the main album.
- [ ] Document why they are excluded from the main album.
- [ ] Explain that they are better suited for other specialized programs.

## Technical programs and ecosystems to document

- [ ] Explain the use of `jsMath` fonts.
- [ ] Explain the use of `LyX` fonts.
- [ ] Explain the use of `LaTeX` fonts.
- [ ] Explain the use of `TeX` fonts.
- [ ] Explain that some depend on special metrics or composition conventions and do not display well in normal HTML.

## System dependencies and clarifications

- [ ] Document that `paquetes-deb` may also contain dependencies and not only font packages.
- [ ] Explain that some dependencies are for rendering, others for typographic composition, and others for specialized programs.
- [ ] Do not assume that all dependencies improve visualization in a normal web browser.

## PyQt6 interface

### Main window

- [x] Show base working folder.
- [x] Show number of detected `.deb` packages.
- [x] Show folder status.
- [x] Show extraction progress.
- [x] Show analysis progress.
- [x] Show HTML generation progress.
- [x] Show card generation progress.
- [ ] Show PDF generation progress.

### Minimum buttons

- [x] `Prepare structure` button.
- [x] `Extract all fonts to album-fuentes` button.
- [x] `Analyze and classify master collection` button.
- [ ] `Generate album-fuentes-espanol` button.
- [ ] `Generate album-fuentes-tecnicas` button.
- [x] `Generate HTML indexes` button.
- [x] `Generate cards` button.
- [ ] `Generate PDFs` button.

### Future interface improvements

- [ ] Integrated output console.
- [ ] Reports panel.
- [ ] Font preview.
- [ ] Base folder selector.
- [ ] Persistent settings.

## Recommended architecture

### Filesystem module

- [x] Create and validate folders.
- [x] Check permissions.
- [ ] Clean or reuse outputs.

### `.deb` package module

- [x] Detect packages.
- [x] Extract with `dpkg-deb -x`.
- [x] Determine whether they contain fonts.

### Typographic analysis module

- [x] Read font metadata.
- [x] Detect Spanish coverage.
- [x] Detect technical fonts.
- [ ] Detect designer-useful filters.

### HTML generation module

- [x] Generate HTML albums by reusing the existing logic.

### Card module

- [x] Generate PNG cards with Pillow.

### PDF module

- [ ] Generate PDF from cards or from direct composition.

### GUI module

- [ ] Orchestrate everything from `PyQt6`.
- [ ] Do not reimplement business logic inside the GUI.

## Reuse of previous work

- [ ] Reuse `generar_album_fuentes.py`.
- [ ] Reuse `generar_album_fuentes_espanol.py`.
- [ ] Reuse `generar_album_fuentes_tecnicas.py`.
- [ ] Reuse `generar_album_fuentes_espanol_imagenes.py` where appropriate.
- [ ] Extract common logic into reusable functions or modules.

## Suggested phases

### Phase 1

- [x] Create the PyQt6 project skeleton.
- [x] Create the minimum main window.
- [x] Implement `Prepare structure`.

### Phase 2

- [x] Implement full extraction into `album-fuentes`.
- [x] Implement error and duplicate logging.

### Phase 3

- [x] Implement analysis of the master collection.
- [x] Implement derivation into Spanish and technical albums.

### Phase 4

- [x] Implement HTML generation from the GUI.
- [x] Implement card generation from the GUI.

### Phase 5

- [ ] Implement PDF generation.
- [ ] Optimize performance.
- [ ] Prevent interface freezing.

### Phase 6

- [ ] Implement new filters useful for designers.
- [ ] Generate additional derived albums.

## Risks and points to review

- [ ] Damaged or incomplete `.deb` packages.
- [ ] Duplicate fonts.
- [ ] Fonts that fail to load with Pillow.
- [ ] Difficulty automatically distinguishing some technical font families.
- [ ] Long rendering times.
- [ ] Need for threads or processes to avoid freezing the GUI.
- [ ] Differences between what Pillow renders and what the browser renders.
- [ ] Differences between fonts that are genuinely good for design and fonts that only seem useful at first glance.

## Expected final result

- [ ] The user prepares the structure with a button.
- [ ] The user manually places the `.deb` files in `paquetes-deb`.
- [ ] The application first extracts everything into `album-fuentes`.
- [ ] The application analyzes that master collection.
- [ ] The application creates derived albums such as Spanish and technical.
- [ ] The application generates HTML, cards, and PDFs.
- [ ] The system is ready to grow with new filters useful for designers.
