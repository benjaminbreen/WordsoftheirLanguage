"""Edition file for Dudley's Italian Trinidad/Guiana word list (BSB Cod.icon. 140, fol. 74v).

Input:  data/work/extract3/dudley_arcano.entries.csv, dudley_img/159.jpg
Output: data/site/manuscripts/dudley.json, site/public/scans/dudley/0159-{900,1800}.webp
"""
import csv
import json
import os

from PIL import Image

SRC = "data/work/extract3/dudley_arcano"
OUT = "data/site/manuscripts/dudley.json"
IMG = "site/public/scans/dudley"

os.makedirs(IMG, exist_ok=True)
im = Image.open("data/work/extract3/dudley_img/159.jpg").convert("RGB")
for w in (900, 1800):
    h = round(im.height * w / im.width)
    im.resize((w, h), Image.LANCZOS).save(f"{IMG}/0159-{w}.webp", quality=80)
entries = []
for i, r in enumerate(csv.DictReader(open(SRC + ".entries.csv", encoding="utf-8")), 1):
    if not (r.get("form_as_printed") or "").strip():
        continue
    entries.append(dict(n=i, hw=r["form_as_printed"].strip(), gloss=(r.get("gloss_as_printed") or "").strip(),
                        en=(r.get("translation_en") or "").strip(), note=(r.get("note") or "").strip(), page=0))
data = dict(archive=dict(url="https://www.digitale-sammlungen.de/view/bsb00084102?page=159",
                         scan_url="https://www.digitale-sammlungen.de/view/bsb00084102?page=",
                         source="Bayerische Staatsbibliothek", rights="Images: Bayerische Staatsbibliothek, MDZ"),
            pages=[dict(scan="159", w=im.width, h=im.height, sm=f"/scans/dudley/0159-900.webp",
                        lg=f"/scans/dudley/0159-1800.webp")],
            entries=entries)
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(entries), "entries")
