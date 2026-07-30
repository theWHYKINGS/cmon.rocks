#!/usr/bin/env python3
"""inject_head.py — add the bits the Claude Design source doesn't carry.

index.html is regenerated from Claude Design on every deploy, so anything we add
by hand is wiped each pull. This re-applies it idempotently:

  * <html lang="de">
  * <title> + meta description + canonical + og/twitter tags
  * favicon / apple-touch-icon
  * footer legal links: the source points them at #impressum / #datenschutz / #agb.
    We repoint Impressum + Datenschutz at the real pages and remove the AGB link
    (no AGB content yet — restore it once terms exist).

Run it after unpack_code.py; deploy.sh does that for you.

    python3 scripts/inject_head.py
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
idx = root / "index.html"
html = idx.read_text(encoding="utf-8")

TITLE = "CMON! Coworking · Maxvorstadt — Familiäres Coworking in München"
DESC = ("Familiäres Coworking in der Münchner Maxvorstadt: feste Bürogemeinschaft "
        "unter der Woche, 24/7-Zugang, 250 Mbit/s, Meetingraum & Fokusbox, "
        "Siebträger-Kaffee. Jetzt Besichtigung anfragen.")
URL = "https://www.cmon.rocks/"

HEAD = f"""<title>{TITLE}</title>
<meta name="description" content="{DESC}" />
<link rel="canonical" href="{URL}" />
<link rel="icon" type="image/png" href="assets/favicon.png" />
<link rel="apple-touch-icon" href="assets/favicon.png" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{TITLE}" />
<meta property="og:description" content="{DESC}" />
<meta property="og:url" content="{URL}" />
<meta property="og:image" content="{URL}assets/hero-lounge.jpg" />
<meta property="og:locale" content="de_DE" />
<meta name="twitter:card" content="summary_large_image" />
"""

changed = []

# 1. <html> -> <html lang="de">
if not re.search(r"<html[^>]*\blang=", html):
    html = re.sub(r"<html\b", '<html lang="de"', html, count=1)
    changed.append('lang="de"')

# 2. head block (marked, so re-runs replace instead of stacking up)
BEGIN, END = "<!-- injected-head:begin -->", "<!-- injected-head:end -->"
block = f"{BEGIN}\n{HEAD}{END}\n"
if BEGIN in html:
    html = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", block, html, flags=re.S)
else:
    i = html.find("<head>")
    if i == -1:
        raise SystemExit("ERROR: no <head> found in index.html")
    html = html[: i + len("<head>")] + "\n" + block + html[i + len("<head>") :]
    changed.append("head block")

# 3. footer legal links
new, n = re.subn(r'href="#impressum"', 'href="legal/Impressum.html"', html)
if n:
    html = new; changed.append("Impressum link")
new, n = re.subn(r'href="#datenschutz"', 'href="legal/Datenschutz.html"', html)
if n:
    html = new; changed.append("Datenschutz link")
# remove the AGB link entirely (no AGB page yet)
new, n = re.subn(r'<a\s+href="#agb"[^>]*>.*?</a>', "", html, flags=re.S)
if n:
    html = new; changed.append(f"removed AGB link ({n})")

idx.write_text(html, encoding="utf-8")
print("✓ inject_head: " + (", ".join(changed) if changed else "already up to date"))
