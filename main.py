#!/usr/bin/env python3
"""Entrypoint for the news-image-20261118 competition entry.

At grade time this program runs in a fresh container with no network,
a read-only repository and only the Python standard library, so it
does the smallest honest job it can: it finds the pre-rendered
``entry.png`` that sits next to it, checks that it really is the
1024x1024 PNG the competition asks for, and copies it into the
output directory the harness provides.

The picture itself is produced by ``draw.py`` (Pillow, build time
only) and is not re-rendered here.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import sys

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"


class EntryError(Exception):
    """Raised when the entry file is missing or fails validation."""


def _read_png_dimensions(path: str) -> tuple:
    """Return (width, height) after checking the PNG signature and IHDR."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE:
        raise EntryError(f"{path}: not a PNG file (bad signature)")
    if header[12:16] != b"IHDR":
        raise EntryError(f"{path}: first chunk is not IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _sha256(path: str) -> str:
    """Stream a file through SHA-256 and return the hex digest."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _output_directory() -> str:
    """Where the harness wants the entry: env var, else a local folder."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"


def run() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source):
        raise EntryError(f"missing entry image: {source}")
    width, height = _read_png_dimensions(source)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise EntryError(
            f"{source}: expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, "
            f"got {width}x{height}"
        )
    outdir = _output_directory()
    os.makedirs(outdir, exist_ok=True)
    target = os.path.join(outdir, SOURCE_NAME)
    shutil.copyfile(source, target)
    before = _sha256(source)
    after = _sha256(target)
    if before != after:
        raise EntryError(f"copy mismatch: {source} -> {target}")
    size = os.path.getsize(target)
    if size > MAX_BYTES:
        raise EntryError(f"{target}: {size} bytes, over the 1 MiB limit")
    print(f"entry.png -> {target} ({size} bytes, sha256 {after})")
    return 0


def main(argv: list | None = None) -> int:
    try:
        return run()
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
