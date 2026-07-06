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

**When deploying changes:** bump the `CACHE` version string at the top of
`sw.js` (e.g. `aatif-fitness-v1` → `-v2`), and add any new asset paths to its
`PRECACHE` list. Without the bump, previously cached files keep being served.

Images are WebP, resized close to their display size. Keep new images in that
format (`cwebp -q 80`, `gif2webp` for animations).

## GitHub Pages

This project is designed to be served as a static site from GitHub Pages.
