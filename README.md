# Aatif Fitness

A small mobile-first reference app for weekly training, meals, daily anchors, and recovery rules.

## Files

- `index.html` contains the app shell and fitness plan data.
- `support.js` contains the generated runtime used by the `.dc.html` export.
- `manifest.webmanifest` adds basic phone install metadata.
- `sw.js` is the service worker that precaches the whole app for offline use.
- `vendor/` holds the local React/ReactDOM bundles (no CDN needed).
- `assets/fonts/` holds the self-hosted webfonts (no Google Fonts request).
- `screenshots/anchors.png` is the included app screenshot.

## Fully offline

Everything the app needs — runtime, fonts, and all images — is served from this
repo and precached by `sw.js` on first visit, so the app works with no network
(e.g. in the gym) once it has loaded once.

`sw.js` is regenerated automatically on every deploy by
`scripts/generate_sw.py`: the precache list is scanned from `index.html`,
`support.js`, and the fonts CSS, and the cache version is a hash of the file
contents — so pushing any change ships a new worker version with no manual
steps. (Run the script yourself only if you want to test locally.)

Images can be committed in any format (PNG/JPG/GIF): on deploy,
`scripts/convert_images.py` converts them to WebP sized near their display
size, rewrites the references in `index.html`, and drops the originals from
the published site. Reference new images by their committed path — the
rewrite is automatic.

## GitHub Pages

Deployed by `.github/workflows/deploy.yml` on every push to `main`: it
converts images to WebP, regenerates `sw.js`, then publishes the result as
the Pages artifact.
