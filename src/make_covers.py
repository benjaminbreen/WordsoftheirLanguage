"""Covers for registry tables that lack one: the first scan page, at the site's two cover widths."""
import json
import os

from PIL import Image

for t in json.load(open("data/site/extra_tables.json", encoding="utf-8")):
    cov = t.get("cover", t["id"])
    if os.path.exists(f"site/public/covers/{cov}-360.webp"):
        continue
    scan = json.load(open(f"data/site/scans/{t['id']}.json"))
    im = Image.open("site/public" + scan["pages"][0]["img"]["1800"]).convert("RGB")
    for s, w in ((360, 360), (720, 576)):
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(f"site/public/covers/{cov}-{s}.webp", quality=82)
    print("cover", cov)
