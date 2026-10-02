# Wordes of their Language — website

Static Astro site. It reads only the pipeline's output in `src/data/tables/*.json` and the images in
`public/scans` and `public/covers`; nothing here edits data.

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # static output in dist/
```

## Deploying on Vercel

Import the repository in Vercel and set **Root Directory** to `site`. Vercel detects Astro;
`vercel.json` sets the build and cache headers. Set the environment variable `SITE_URL` to the
production URL so the sitemap and canonical links are right.

## Adding or updating tables

From the repository root (Python pipeline):

```bash
PYTHONPATH=src .venv/bin/python src/scans.py <table-id>   # locate pages, align entries, write images
PYTHONPATH=src .venv/bin/python src/build_site_v2.py      # write site/src/data/tables/*.json
```

Then commit and push; Vercel rebuilds. New tables are declared in `TABLES` (src/scans.py) and `T`
(src/build_site_v2.py).

## Layout of the data

- `src/data/tables/<id>.json` — one table: provenance, page images, entries (form/gloss as printed,
  concepts, position on the page, draft note), identification. Schema version in `schema`.
- `public/scans/<id>/<leaf>-{900,1800}.webp` — page images; `public/covers/*.webp` — title pages.
- Built endpoints: `/t/<id>/entries.csv`, `/t/<id>/entries.json`, `/data/index.json` (search index).

Page images currently live in the repository (~45 MB). Past a few hundred tables, move `public/scans`
to object storage (Cloudflare R2 or Vercel Blob) and point the image paths at it.

## Things to set

- `src/config.ts` → `REPO_URL` turns on "open an issue" links for corrections.
