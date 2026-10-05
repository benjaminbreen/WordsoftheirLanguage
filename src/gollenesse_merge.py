"""Merge proofread batches of Stein van Gollenesse's 1743 Malabar glossary into one edition file.

Input:  data/work/voc_register/gollenesse/entries_{A_proofed,B1_proofed,B2_proofed,C1_proofed,C2_proofed,D}.jsonl
Output: data/work/voc_register/gollenesse/glossary.json
"""
import json

D = "data/work/voc_register/gollenesse"
PARTS = ["A_proofed", "B1_proofed", "B2_proofed", "C1_proofed", "C2_proofed", "D"]


def main():
    out = []
    for p in PARTS:
        rows = [json.loads(l) for l in open(f"{D}/entries_{p}.jsonl", encoding="utf-8") if l.strip()]
        for r in rows:
            hw = (r.get("headword") or "").strip()
            if out and r.get("continues_from_previous_page") and not hw:
                # tail of an entry begun in the previous batch
                out[-1]["dutch"] = out[-1]["dutch"].rstrip() + " | " + r["dutch"].strip()
                out[-1]["translation_en"] = (out[-1].get("translation_en") or "") + " " + (r.get("translation_en") or "")
                out[-1]["notes"] = (out[-1].get("notes") or "") + " / " + (r.get("notes") or "")
                continue
            if out and hw and hw == out[-1]["headword"] and r["scan"] == out[-1]["scan"]:
                out[-1] = r  # same entry in two batches (boundary overlap): keep the later, fuller version
                continue
            out.append(r)
    for i, r in enumerate(out, 1):
        r["n"] = i
        r["kind"] = "section" if not (r.get("headword") or "").strip() else "entry"
    json.dump(out, open(f"{D}/glossary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ents = [r for r in out if r["kind"] == "entry"]
    print(len(out), "records,", len(ents), "entries")
    return out



SITE = "data/site/manuscripts/gollenesse.json"


def ident(x):
    """Proposed modern identification; Malayalam script shown only at high confidence."""
    if not x or not (x.get("modern") or "").strip():
        return None
    return dict(modern=x["modern"].strip(), cat=x.get("category") or "", where=x.get("location") or "",
                conf=x.get("confidence") or "low", basis=x.get("basis") or "",
                ml=(x.get("malayalam") or "") if x.get("confidence") == "high" else "")


def build_site(records):
    import os
    pages = json.load(open(f"{D}/web_pages.json"))
    idx = {p["scan"]: i for i, p in enumerate(pages)}
    ids = {}
    if os.path.exists(f"{D}/ids_reviewed.jsonl"):
        for l in open(f"{D}/ids_reviewed.jsonl", encoding="utf-8"):
            if l.strip():
                x = json.loads(l)
                ids[x["n"]] = x
    entries = []
    for r in records:
        if r["kind"] != "entry":
            continue
        scans = [r["scan"]]
        # entries running over a page break also show on the following scan(s)
        for _ in range(r["dutch"].count(" | ")):
            nxt = [p["scan"] for p in pages if p["scan"] > scans[-1]]
            if nxt:
                scans.append(nxt[0])
        entries.append(dict(
            n=len(entries) + 1, hw=r["headword"].strip().rstrip(","), nl=r["dutch"].replace(" | ", " "),
            en=(r.get("translation_en") or "").strip(), folio=r.get("folio") or "",
            page=idx.get(r["scan"], 0), pages=[idx[s] for s in scans if s in idx],
            refs=r.get("cross_refs") or [], doubt="[?]" in r["dutch"] or "[...]" in r["dutch"],
            id=ident(ids.get(r["n"]))))
    data = dict(
        id="gollenesse", title="Mallabars woordenboek",
        subtitle="An alphabetical glossary of Malabar, appended to the memoir of J. V. Stein van Gollenesse",
        place="Cochin", year=1743, author="Julius Valentijn Stein van Gollenesse",
        archive=dict(holder="Nationaal Archief, The Hague", ref="1.04.02 (VOC), inv. 2601, fol. 161–191",
                     url="https://www.nationaalarchief.nl/onderzoeken/archief/1.04.02/invnr/2601",
                     scan_url="https://www.nationaalarchief.nl/onderzoeken/archief/1.04.02/invnr/2601/file/NL-HaNA_1.04.02_2601_"),
        pages=[dict(scan=p["scan"], w=p["w"], h=p["h"], sm=f"/scans/gollenesse/{p['scan']}-900.webp",
                    lg=f"/scans/gollenesse/{p['scan']}-1800.webp") for p in pages],
        entries=entries)
    os.makedirs(os.path.dirname(SITE), exist_ok=True)
    json.dump(data, open(SITE, "w", encoding="utf-8"), ensure_ascii=False)
    print(SITE, len(entries), "entries,", sum(e["doubt"] for e in entries), "with uncertain readings")


if __name__ == "__main__":
    build_site(main())
