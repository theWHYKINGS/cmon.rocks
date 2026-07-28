#!/usr/bin/env python3
"""unpack_code.py — decode an cm_code.json bundle (source HTML + support.js +
design-system files) pulled from the Claude Design Academy project into the repo.

Same "build from live source" path as the main site: the page is hosted as its
Claude Design source (client-rendered) plus its dependencies, so it always
reflects the current design without waiting for an offline re-export.

The source file "Academy Redesign.dc.html" is written as index.html.

    python3 scripts/unpack_code.py [path/to/cm_code.json]
    (defaults to the newest ~/Downloads/cm_code*.json)
"""
import base64
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# Chrome saves repeat downloads as "cm_code (1).json", "cm_code (2).json", …
# so default to the NEWEST cm_code*.json, not a fixed name (else we'd unpack a
# stale bundle and silently deploy nothing).
if len(sys.argv) > 1:
    src = Path(sys.argv[1])
else:
    matches = sorted(Path.home().glob("Downloads/cm_code*.json"), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise SystemExit("No cm_code*.json found in ~/Downloads")
    src = matches[-1]
print(f"reading {src.name}")

data = json.loads(src.read_text(encoding="utf-8"))

# The entry file gets renamed to index.html. Do NOT hardcode its name — it has
# already changed once ("Academy Redesign.dc.html" -> "Academy Deploy.dc.html")
# and a fixed name would silently publish a stale index.html. The entry is the
# only top-level .html in the bundle; everything else lives in a subfolder.
entries = [p for p in data if p.lower().endswith(".html") and "/" not in p]
if len(entries) > 1:
    # The project also holds the offline export ("theWHYKINGS Academy.html",
    # ~1.4 MB, <title>Bundled Page</title>) which we must never publish — the
    # editable source is the .dc.html one.
    dc = [p for p in entries if p.lower().endswith(".dc.html")]
    if len(dc) == 1:
        entries = dc
if len(entries) != 1:
    raise SystemExit(f"Expected exactly one source .html in the bundle, got: {entries}")
RENAME = {entries[0]: "index.html"}
print(f"entry: {entries[0]} -> index.html")

count = 0
for rel, obj in data.items():
    out = RENAME.get(rel, rel)
    dest = (root / out).resolve()
    if root not in dest.parents:
        print(f"  ! skipped (outside repo): {rel}")
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(obj["content"]))
    count += 1
print(f"✓ wrote {count} code files (source -> index.html)")
