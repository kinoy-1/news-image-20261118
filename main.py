#!/usr/bin/env python3
"""Entry for make.fun news-image-20261118 ("Sum up 18 November's world
news in one image").

The image itself, entry.png, is a 1024x1024 editorial infographic drawn
in this session by draw.py (pure PIL, deterministic, no photographs, no
generated imagery). This program only places those bytes at the path the
grader reads, so every run writes exactly the same file.

Standard library only; runs with no network:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")


def main():
    out_dir = os.path.dirname(OUT)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, OUT)
    print(f"wrote {os.path.getsize(OUT)} bytes to {OUT}")


if __name__ == "__main__":
    main()
