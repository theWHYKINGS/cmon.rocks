#!/usr/bin/env python3
"""unpack_images.py — decode a cm_images.json bundle (pulled from Claude Design
via the browser) into the repo's assets/ and uploads/ folders.

The current Claude Design export references images by relative path instead of
inlining them, so the referenced image files must be hosted alongside the HTML.
Claude fetches them in the browser into a single JSON bundle (path -> base64);
this script writes them to disk. Re-run whenever the image set changes.

    python3 scripts/unpack_images.py [path/to/cm_images.json]
    (defaults to ~/Downloads/cm_images.json)
"""
import base64
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent

# Default to the NEWEST cm_images*.json (Chrome appends "(1)", "(2)", … to
# repeat downloads, so a fixed name would read a stale bundle).
if len(sys.argv) > 1:
    src = Path(sys.argv[1])
else:
    matches = sorted(Path.home().glob("Downloads/cm_images*.json"), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise SystemExit("No cm_images*.json found in ~/Downloads")
    src = matches[-1]

data = json.loads(src.read_text(encoding="utf-8"))
count = 0
total = 0
for rel, obj in data.items():
    dest = (root / rel).resolve()
    if root not in dest.parents:           # guard against path escapes
        print(f"  ! skipped (outside repo): {rel}")
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = base64.b64decode(obj["content"])
    dest.write_bytes(raw)
    count += 1
    total += len(raw)
print(f"✓ wrote {count} image files ({total/1048576:.2f} MB) into assets/ + uploads/")
