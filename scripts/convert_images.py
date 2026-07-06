#!/usr/bin/env python3
"""Convert any PNG/JPG/GIF under assets/ to right-sized WebP and rewrite
references in index.html. Runs in CI before generate_sw.py, so committed
images can stay in their original format — the deployed site always serves
WebP. Requires cwebp and gif2webp on PATH.

Max heights are chosen per directory to match how large the app actually
displays each image class (see index.html)."""

import pathlib
import re
import struct
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (path glob relative to repo root, max pixel height)
SIZE_RULES = [
    ("assets/workouts/*", 640),          # today-card hero, shown 128x158
    ("assets/exercises/thumbs/*", 222),  # list thumbnails, shown 58x74
    ("assets/exercises/samples/*/frame-1-full.*", 222),
    ("assets/exercises/samples/*", 1400),
    ("assets/exercises/*-guide.*", 1020),  # expanded media, max-height 340
]
DEFAULT_MAX_HEIGHT = 1400
QUALITY = "80"


def image_height(path: pathlib.Path) -> int:
    data = path.open("rb").read(64 * 1024)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">I", data[20:24])[0]
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<H", data[8:10])[0]
    if data[:2] == b"\xff\xd8":  # JPEG: scan for a SOF marker
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return struct.unpack(">H", data[i + 5 : i + 7])[0]
            i += 2 + struct.unpack(">H", data[i + 2 : i + 4])[0]
    raise ValueError(f"cannot read dimensions of {path}")


def max_height_for(rel: str) -> int:
    for pattern, maxh in SIZE_RULES:
        if pathlib.PurePosixPath(rel).match(pattern):
            return maxh
    return DEFAULT_MAX_HEIGHT


def convert(path: pathlib.Path) -> pathlib.Path:
    rel = path.relative_to(ROOT).as_posix()
    out = path.with_suffix(".webp")
    if path.suffix.lower() == ".gif":
        cmd = ["gif2webp", "-quiet", "-q", QUALITY, "-mixed", str(path), "-o", str(out)]
    else:
        cmd = ["cwebp", "-quiet", "-q", QUALITY]
        maxh = max_height_for(rel)
        if image_height(path) > maxh:
            cmd += ["-resize", "0", str(maxh)]
        cmd += [str(path), "-o", str(out)]
    subprocess.run(cmd, check=True)
    return out


def main() -> int:
    candidates = [
        p
        for p in sorted((ROOT / "assets").rglob("*"))
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif")
        and "fonts" not in p.relative_to(ROOT).parts
    ]
    if not candidates:
        print("convert_images: nothing to convert (all WebP already)")
        return 0

    index = ROOT / "index.html"
    html = index.read_text()
    for src in candidates:
        out = convert(src)
        old_ref = "./" + src.relative_to(ROOT).as_posix()
        new_ref = "./" + out.relative_to(ROOT).as_posix()
        n = html.count(old_ref)
        html = html.replace(old_ref, new_ref)
        src.unlink()  # keep the original out of the deploy artifact
        print(f"converted {old_ref} -> {new_ref} ({n} reference(s) rewritten)")
    index.write_text(html)

    leftovers = re.findall(r"\./assets/[^'\"\s)]+\.(?:png|jpe?g|gif)", html)
    if leftovers:
        print("ERROR: references to non-WebP images remain:", *set(leftovers), sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
