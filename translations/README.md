# Translation workflow

## Files

- `fontgallery_en.ts`
- `fontgallery_es.ts`
- `fontgallery_en.qm`
- `fontgallery_es.qm`

## Update source strings

Run:

```bash
./translations/update_translations.sh
```

This does two things:

1. updates the `.ts` files from the Python source code with `pylupdate6`;
2. compiles the `.qm` runtime files with `lrelease`.

## Editing translations

To edit translations with Qt Linguist:

```bash
linguist translations/fontgallery_es.ts
```

You can do the same with `fontgallery_en.ts` if you want an explicit English catalog, but the application already uses English source strings as its default UI language.

## Runtime behavior

- English is the source language of the application.
- Spanish is loaded from `translations/fontgallery_es.qm` when the system locale is Spanish.
- If a `.qm` file is missing, the application falls back to English source strings.
