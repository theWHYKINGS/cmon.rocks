#!/usr/bin/env python3
"""build_legal.py — turn the legal sources (src/legal/*.html) into clean,
self-contained pages served at legal/Impressum.html + legal/Datenschutz.html.

The sources link to legal.css and carry a text wordmark. This inlines legal.css,
applies the CMON theme (terracotta accent + cream background) via :root variable
overrides, wires up the locally vendored fonts (vendor/fonts-local.css), and
writes the finished pages under legal/.

Re-run after editing the legal text:
    python3 scripts/build_legal.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
legal_css = (root / "src/legal/legal.css").read_text(encoding="utf-8")

# CMON theme: retint the gold/Jost defaults in legal.css to the site's
# terracotta + cream palette and its Hanken Grotesk / Newsreader fonts.
theme_css = """
/* injected by build_legal.py — CMON theme + text wordmark */
:root{
  --neutral-50:#FAF6EE; --neutral-800:#241E17; --neutral-600:#4A4038;
  --neutral-500:#6B6055; --color-gold:#A65231; --gold-600:#A65231;
  --font-body:'Hanken Grotesk',system-ui,sans-serif;
  --font-display:'Newsreader',Georgia,serif;
}
.legal-bar a{text-decoration:none;}
.legal-wordmark{font-family:var(--font-display);font-weight:600;
  font-size:22px;line-height:1;color:#EFE7DA;text-decoration:none;letter-spacing:.01em;}
"""

# the legal pages sit in legal/, so ../vendor reaches the vendored font css
fonts_link = '<link rel="stylesheet" href="../vendor/fonts-local.css" />'
style_block = f"{fonts_link}\n<style>\n{legal_css}\n{theme_css}\n</style>"

pages = [
    ("src/legal/Impressum.html", "legal/Impressum.html"),
    ("src/legal/Datenschutz.html", "legal/Datenschutz.html"),
]

for src, out in pages:
    html = (root / src).read_text(encoding="utf-8")
    # inline legal.css (+ theme + local fonts) in place of the <link>
    html, n = re.subn(r'<link[^>]*href="legal\.css"[^>]*>', lambda m: style_block, html)
    if n != 1:
        print(f"  ! {src}: expected exactly one legal.css <link>, found {n}")
    (root / out).parent.mkdir(parents=True, exist_ok=True)
    (root / out).write_text(html, encoding="utf-8")

    leftover = [p for p in ("legal.css", "googleapis", "gstatic") if p in html]
    status = ("  ⚠ leftover refs: " + ", ".join(leftover)) if leftover else "  — self-contained"
    print(f"✓ {out} ({len(html)} bytes){status}")
