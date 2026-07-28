# cmon.rocks

Marketing site for **CMON! Coworking · Maxvorstadt**, hosted on GitHub Pages
(`theWHYKINGS/cmon.rocks`, custom domain `www.cmon.rocks`).

Like the other WHYKINGS sites, this is built from a **Claude Design** project and
hosted as the live source (client-rendered `index.html` + `support.js`), so it
always reflects the current design.

## Deploy loop

You say **"deploy cmon"**; Claude pulls the latest source out of Claude Design
via the authenticated browser session, unpacks it, and pushes here. See
[`scripts/pull-from-design.md`](scripts/pull-from-design.md) for the full
protocol and the still-open pre-launch items (legal pages, `<title>`/SEO, fonts).

```bash
python3 scripts/unpack_code.py        # newest ~/Downloads/cm_code*.json -> index.html
python3 scripts/unpack_images.py      # only when images changed
scripts/deploy.sh "what changed"      # commit + push + request a Pages build
```

## Design project

`0517deb9-ca31-46e2-a79d-ecb1c8669be7` — entry `CMON Website 1a Template.dc.html`.
