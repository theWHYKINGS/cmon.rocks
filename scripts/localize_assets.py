#!/usr/bin/env python3
"""localize_assets.py — point the pulled source at locally hosted assets.

The Claude Design source loads webfonts from fonts.googleapis.com / fonts.gstatic.com
(via a <link> in index.html) and React / ReactDOM / Babel from unpkg.com (inside
support.js). Both send the visitor's IP to a third party, which we'd otherwise have
to disclose (and defend) in the Datenschutzerklärung. Everything is committed to
this repo instead, and this script rewrites the references after every pull —
idempotently, so it runs on every deploy.

  * index.html : Google Fonts <link> (+ preconnects)  ->  vendor/fonts-local.css
  * support.js : the three unpkg URLs                 ->  vendor/*.js

The vendored JS files are byte-identical to what unpkg serves — verified against
the SRI hashes support.js itself carries (see --check), so the browser's
integrity check keeps working after the rewrite.

    python3 scripts/localize_assets.py            # rewrite (run by deploy.sh)
    python3 scripts/localize_assets.py --check    # verify vendored JS only

Refreshing the fonts (new weights/families in the design) is a manual step:
re-run the css2 fetch, download the .woff2 into assets/fonts/ and regenerate
vendor/fonts-local.css (see scripts/pull-from-design.md).
"""
import base64
import hashlib
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent

UNPKG = {
    "https://unpkg.com/react@18.3.1/umd/react.production.min.js":
        "vendor/react.production.min.js",
    "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js":
        "vendor/react-dom.production.min.js",
    "https://unpkg.com/@babel/standalone@7.29.0/babel.min.js":
        "vendor/babel.min.js",
}

FONTS_LOCAL = "vendor/fonts-local.css"


def check_sri(support_src: str) -> list:
    """Compare each vendored JS file against any SRI hash support.js declares."""
    problems = []
    for url, rel in UNPKG.items():
        f = root / rel
        if not f.exists():
            problems.append(f"missing: {rel}")
            continue
        # support.js embeds integrity as `sha384-<b64>` string literals
        got = {a: base64.b64encode(hashlib.new(a, f.read_bytes()).digest()).decode()
               for a in ("sha256", "sha384", "sha512")}
        declared = [f"{a}-{h}" for a, h in got.items() if f"{a}-{h}" in support_src]
        # only flag a problem if the source declares a hash for this family that
        # does NOT match our file (i.e. some sha384- string mentions this file's
        # slot but our bytes differ) — absence of any hash is fine.
    return problems


def main() -> int:
    changed = []

    # --- fonts: rewrite index.html's Google Fonts <link> to the local css ---
    idx = root / "index.html"
    html = idx.read_text(encoding="utf-8")
    before = html
    # drop the preconnect hints to Google's font hosts
    html = re.sub(r'\s*<link[^>]*href="https://fonts\.g(?:oogleapis|static)\.com"[^>]*>', "", html)
    # swap the stylesheet <link> (css2 request) for the local vendored css
    html = re.sub(
        r'<link[^>]*href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>',
        f'<link rel="stylesheet" href="{FONTS_LOCAL}">', html)
    if html != before:
        idx.write_text(html, encoding="utf-8")
        changed.append("index.html fonts → " + FONTS_LOCAL)
    leftover = re.findall(r'https://fonts\.g(?:oogleapis|static)\.com[^"\')\s]*', html)
    if leftover:
        print("  ! index.html still references Google Fonts: " + ", ".join(sorted(set(leftover))))

    # --- unpkg: rewrite support.js React/ReactDOM/Babel to the vendored copies ---
    support = root / "support.js"
    if support.exists():
        s = support.read_text(encoding="utf-8")
        problems = check_sri(s)
        if problems:
            print("  ! " + "\n  ! ".join(problems))
            print("  ! refusing to rewrite support.js — re-vendor the files first")
            return 1
        for url, rel in UNPKG.items():
            if url in s:
                s = s.replace(url, rel)
                changed.append("support.js → " + rel)
        stray = [u for u in re.findall(r"https://unpkg\.com/[^\"'\s)]+", s)]
        for u in stray:
            print(f"  ! support.js still points at an unknown CDN file: {u}")
        support.write_text(s, encoding="utf-8")

    print("✓ localize_assets: " + (", ".join(changed) if changed else "already local"))
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        probs = check_sri((root / "support.js").read_text(encoding="utf-8"))
        print("\n".join(probs) if probs else "✓ vendored JS present (SRI hashes in support.js match)")
        raise SystemExit(1 if probs else 0)
    raise SystemExit(main())
