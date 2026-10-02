"""Assemble the site's data: one JSON per table + a catalogue + a search index.

Inputs
  data/work/extract*/<list>.entries.csv     diplomatic transcriptions
  data/site/scans/<table>.json              page images + entry boxes (src/scans.py)
  out/site/data.json                        identifications (src/build_site_data.py)
  data/work/encounter/annot*/*.jsonl        draft notes (protocol annotations)
  out/cases/herbert_vs_vanneck_alignment.csv
Outputs
  site/src/data/tables/<id>.json, site/src/data/catalog.json, site/public/data/search.json
"""
import csv
import glob
import json
import os
import re
import unicodedata

import polars as pl

from identify2 import ConceptMapper
import glottolog

OUT = "site/src/data"
SCHEMA_VERSION = 1

# id -> csv path, filter, annotation list id, identification id, cover, region, language, glottocode, book
T = {
    "rosier": dict(csv="data/work/extract/rosier_A71306", ann="rosier", ident="rosier", cover="purchas4",
                   region="North America", lang="Eastern Abenaki", glotto="east2544",
                   short="Purchas his Pilgrimes, part 4", author="Samuel Purchas (ed.)", collector="James Rosier",
                   place="St George's River, Maine", heard="1605", printed=1625, tcp="A71306"),
    "wood": dict(csv="data/work/extract/wood_A15685", ann="wood", ident="wood", cover="wood",
                 region="North America", lang="Massachusett", glotto="wamp1249",
                 heading="Because many have desired to heare some of the Natives Language, I have here inserted a small Nomenclator",
                 short="New Englands Prospect", author="William Wood", collector="William Wood",
                 place="Massachusetts Bay", heard="c. 1629–33", printed=1634, tcp="A15685"),
    "williams": dict(csv="data/work/extract/williams_A66450", ann="williams", ident="williams", cover="williams",
                     region="North America", lang="Narragansett", glotto="narr1280",
                     short="A Key into the Language of America", author="Roger Williams", collector="Roger Williams",
                     place="Narragansett Bay", heard="1630s", printed=1643, tcp="A66450",
                     partial="Chapters I–II only (the first 200 entries); the rest of the Key is still to be transcribed."),
    "smith": dict(csv="data/work/extract/smith_map_A12466", ann="smith_map", ident="smith_map", cover="smith",
                  region="North America", lang="Powhatan", glotto="powh1243",
                  short="A Map of Virginia", author="John Smith", collector="John Smith",
                  place="Chesapeake, Virginia", heard="1607–09", printed=1612, tcp="A12466"),
    "cartier": dict(csv="data/work/extract/cartier_A18057", ann="cartier", ident="cartier", cover="cartier",
                    region="North America", lang="Laurentian", glotto="laur1250",
                    short="A Shorte and Briefe Narration", author="Jacques Cartier, trans. John Florio", collector="Jacques Cartier",
                    place="Stadacona and Hochelaga, St Lawrence", heard="1535–36", printed=1580, tcp="A18057"),
    "rochefort": dict(csv="data/work/extract/rochefort_A57484", ann="rochefort", ident="rochefort", cover="rochefort",
                      region="Caribbean & South America", lang="Island Carib", glotto="isla1278", heading="A Caribbian Vocabulary",
                      short="The History of the Caribby-Islands", author="César de Rochefort, trans. John Davies",
                      collector="César de Rochefort", place="Lesser Antilles", heard="before 1658", printed=1666, tcp="A57484"),
    "trinidad": dict(csv="data/work/extract2/trinidad_A02495", ann="trinidad", ident="trinidad", cover="hakluyt3",
                     region="Caribbean & South America", lang="Lokono (Arawak)", glotto="araw1276",
                     short="The Principal Navigations, vol. 3", author="Richard Hakluyt (ed.)", collector="Robert Dudley's voyage",
                     place="Trinidad", heard="1595", printed=1600, tcp="A02495"),
    "chile": dict(csv="data/work/extract2/chilesian_ogilby_A53222", ann="chilesian", ident="chilesian", cover="ogilby",
                  region="Caribbean & South America", lang="Mapudungun", glotto="mapu1245",
                  short="America", author="John Ogilby", collector="Elias Herckmans's expedition",
                  place="Valdivia, Chile", heard="1643", printed=1671, tcp="A53222"),
    "tupi": dict(csv="data/work/extract2/tupi_ogilby_A53222", ann="tupi_ogilby", ident="tupi_ogilby", cover="ogilby",
                 region="Caribbean & South America", lang="Tupinambá", glotto="tupi1273", heading=None,
                 short="America", author="John Ogilby", collector="via Dutch Brazil sources",
                 place="Brazil", heard="17th century", printed=1671, tcp="A53222"),
    "scheffer": dict(csv="data/work/extract/scheffer_A62332", filt="lapland", ann="scheffer", ident="scheffer", cover="scheffer",
                     region="Arctic & North", lang="Sami", glotto="saam1281",
                     short="The History of Lapland", author="Johannes Scheffer", collector="Johannes Scheffer",
                     place="Lapland", heard="compiled 1673", printed=1674, tcp="A62332"),
    "burrough": dict(csv="data/work/extract2/sami_burrough_A02495", ann="sami_burrough", ident="sami_burrough", cover="hakluyt1",
                     region="Arctic & North", lang="Kildin Sami", glotto="kild1236",
                     short="The Principal Navigations, vol. 1", author="Richard Hakluyt (ed.)", collector="Stephen Burrough",
                     place="Kola coast", heard="1557", printed=1599, tcp="A02495"),
    "greenland": dict(csv="data/work/extract2/greenland_olearius_A53322", ann="greenland", ident="greenland", cover="olearius",
                      region="Arctic & North", lang="Kalaallisut (Greenlandic)", glotto="kala1399",
                      short="The Voyages and Travells of the Ambassadors", author="Adam Olearius, trans. John Davies",
                      collector="Adam Olearius", place="Greenlanders brought to Denmark", heard="1654–56", printed=1669, tcp="A53322"),
    "boothby": dict(csv="data/work/extract/boothby_A28809", ann="boothby", ident="boothby", cover="boothby",
                    region="Africa & Indian Ocean", lang="Malagasy", glotto="mala1537",
                    short="A Briefe Discovery … of Madagascar", author="Richard Boothby", collector="Richard Boothby",
                    place="St Augustine's Bay, Madagascar", heard="c. 1630", printed=1647, tcp="A28809"),
    "ludolf": dict(csv="data/work/extract2/ludolf_gallan_A49450", ann="ludolf_gallan", ident="ludolf_gallan", cover="ludolf",
                   region="Africa & Indian Ocean", lang="Ge'ez, Amharic and Oromo", glotto="west2721",
                   short="A New History of Ethiopia", author="Hiob Ludolf", collector="Hiob Ludolf, with Abba Gregorius",
                   place="Ethiopia", heard="1650s", printed=1682, tcp="A49450",
                   partial="Transcribed from the 1682 edition; the scan shown is of the 1684 second edition."),
    "knox": dict(csv="data/work/extract/knox_A47586", ann="knox", ident="knox", cover="knox",
                 region="Asia", lang="Sinhala", glotto="sinh1246",
                 short="An Historical Relation of the Island Ceylon", author="Robert Knox", collector="Robert Knox",
                 place="Kandy, Ceylon", heard="1660–79", printed=1681, tcp="A47586"),
    "vanneck": dict(csv="data/work/extract/vanneck_A08052", ann="vanneck", ident="vanneck", cover="vanneck",
                    region="Asia", lang="Malay", glotto="stan1306",
                    short="The Iournall, or Dayly Register", author="Jacob van Neck (trans.)", collector="Second Dutch voyage",
                    place="Bantam, Java and the Moluccas", heard="1598–99", printed=1601, tcp="A08052"),
    "herbert": dict(csv="data/work/extract/herbert_A03065", ann=None, ident=None, cover="herbert",
                    region="Asia", lang="Malay", glotto="stan1306",
                    short="A Relation of Some Yeares Travaile", author="Thomas Herbert", collector="Thomas Herbert (copied)",
                    place="presented as from the East Indies", heard="copied from a 1598–99 list", printed=1634, tcp="A03065",
                    relation=dict(kind="copied-from", table="vanneck",
                                  text="Herbert's list is a re-sorted copy of the 1601 English van Neck vocabulary: 226 of 243 forms match, and about 70 carry a different English meaning.")),
    "pegu": dict(csv="data/work/extract2/pegu_A21094", ann="pegu", ident="pegu", cover="pegu",
                 region="Asia", lang="Mon", glotto="monn1252",
                 short="A True and Large Discourse of the Voyage", author="anonymous", collector="First East India Company fleet",
                 place="collected from Peguans met in port", heard="1601–02", printed=1603, tcp="A21094"),
    "gthomas": dict(csv="data/work/extract2/gthomas_A64548", ann="gthomas", ident="gthomas", cover="gthomas",
                    region="North America", lang="Pidgin Delaware", glotto="pidg1246",
                    short="An Historical and Geographical Account of Pensilvania", author="Gabriel Thomas", collector="Gabriel Thomas",
                    place="Pennsylvania and West New Jersey", heard="1680s–90s", printed=1698, tcp="A64548"),
}

CAT_LABEL = {"loan": "Loanword", "ostension": "Related meaning", "interactional": "Phrase taken for a word",
             "inflected": "Possessed or inflected form", "wrong_language": "Another language",
             "print_error": "Printing or translation slip"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def fold(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if c.isalnum() or c == " ")
    return (s.replace("ſ", "s").replace("vv", "w").replace("v", "u").replace("j", "i").replace("y", "i")
            .replace("ck", "k").replace("ph", "f"))


def load_annotations():
    best = {}
    for f in sorted(glob.glob("data/work/encounter/annot/*.jsonl")) + sorted(glob.glob("data/work/encounter/annot2/*.jsonl")):
        second = "annot2" in f
        for l in open(f):
            if not l.strip():
                continue
            a = json.loads(l)
            k = (a["list"], int(a["n"]))
            cat = a.get("category")
            if cat not in CAT_LABEL:
                continue
            conf = float(a.get("confidence") or 0)
            verified = "verified" in (a.get("comment") or "")
            if k in best and best[k]["category"] == cat:
                best[k]["agree"] = True
                if verified and not best[k].get("verified"):
                    best[k].update(comment=a.get("comment"), evidence=a.get("evidence"), verified=True)
                continue
            score = conf + (0.15 if verified else 0)
            if k not in best or score > best[k]["score"]:
                best[k] = dict(category=cat, subtype=a.get("subtype"), evidence=a.get("evidence"), comment=a.get("comment"),
                               score=score, verified=verified, agree=False, second=second)
    return {k: v for k, v in best.items() if v["score"] >= 0.6 or v["agree"]}


def clean_comment(c):
    c = re.sub(r"\s*verified:.*$", "", c or "", flags=re.I).strip()
    c = re.sub(r"\s*memory\.?$", "", c, flags=re.I).strip()
    return c


def herbert_notes():
    p = "out/cases/herbert_vs_vanneck_alignment.csv"
    out = {}
    if not os.path.exists(p):
        return out
    for r in csv.DictReader(open(p)):
        key = (r["h_gloss"], r["h_form"])
        fs, gs = float(r["form_sim"]), float(r["gloss_sim"])
        if fs >= 80 and gs < 50:
            out[key] = dict(category="print_error", text=f"Copied from van Neck (1601), where this form means “{r['vn_gloss'].strip(' .,')}” ({r['vn_form']}). Herbert gives it a different meaning.")
        elif fs >= 80:
            out[key] = dict(category="copied", text=f"Copied from van Neck (1601): {r['vn_gloss'].strip(' .,')}, {r['vn_form']}.")
    return out


def interpolate(entries, pages):
    """Estimate positions for unmatched entries that sit between two matched ones on the same column."""
    idx = [i for i, e in enumerate(entries) if e.get("box")]
    for a, b in zip(idx, idx[1:]):
        if b - a < 2 or b - a > 6:
            continue
        A, B = entries[a]["box"], entries[b]["box"]
        if A["page"] != B["page"] or abs(A["x"] - B["x"]) > 0.08 or B["y"] <= A["y"]:
            continue
        for k in range(a + 1, b):
            t = (k - a) / (b - a)
            entries[k]["box"] = dict(page=A["page"], x=A["x"], y=round(A["y"] + t * (B["y"] - A["y"]), 4),
                                     w=max(A["w"], B["w"]), h=A["h"], approx=True)


def main():
    os.makedirs(f"{OUT}/tables", exist_ok=True)
    os.makedirs("site/public/data", exist_ok=True)
    cm = ConceptMapper()
    ann = load_annotations()
    hn = herbert_notes()
    ident = {v["id"]: v for v in json.load(open("out/site/data.json"))["vocabularies"]}
    meta = pl.read_parquet("data/work/meta.parquet")
    md = {r["tcp_id"]: r for r in meta.iter_rows(named=True)}
    catalog, search = [], []
    for tid, c in T.items():
        rows = list(csv.DictReader(open(c["csv"] + ".entries.csv", encoding="utf-8")))
        scan = json.load(open(f"data/site/scans/{tid}.json"))
        boxes = scan["boxes"]
        # trim scan pages without matches at the ends
        used = sorted({b["page"] for b in boxes.values()}) or [0]
        keep = list(range(used[0], used[-1] + 1))
        remap = {p: i for i, p in enumerate(keep)}
        pages = [dict(leaf=scan["pages"][p]["leaf"], w=scan["pages"][p]["w"], h=scan["pages"][p]["h"],
                      sm=scan["pages"][p]["img"]["900"], lg=scan["pages"][p]["img"]["1800"]) for p in keep]
        entries, labels, heads = [], set(), []
        for i, r in enumerate(rows, 1):
            if c.get("filt") and c["filt"] not in (r.get("form_language_label_as_printed") or "").lower():
                continue
            g, f = (r.get("gloss_as_printed") or "").strip(), (r.get("form_as_printed") or "").strip()
            if not f:
                continue
            e = dict(n=i, form=f, gloss=g, section=(r.get("section_heading") or "").strip())
            lab = (r.get("form_language_label_as_printed") or "").strip()
            if lab:
                labels.add(lab)
                if tid == "ludolf":
                    e["col"] = lab
            sec = re.sub(r"\s*\|.*$", "", e["section"]).strip()
            printed_head = sec and not sec.startswith("(") and len(sec) > 2 and not sec.lower().startswith("alphabet of")
            if printed_head and sec not in heads:
                heads.append(sec)
            if not printed_head:
                e["section"] = ""
            cs = sorted(cm(g))
            if cs:
                e["concepts"] = cs
            b = boxes.get(str(i))
            if b and b["page"] in remap:
                x, y, w, h = b["box"]
                e["box"] = dict(page=remap[b["page"]], x=x, y=y, w=w, h=h)
            note = None
            if c.get("ann") and (c["ann"], i) in ann:
                a = ann[(c["ann"], i)]
                note = dict(kind=a["category"], label=CAT_LABEL[a["category"]], text=clean_comment(a["comment"]),
                            compare=(a.get("evidence") or "").strip() or None,
                            checked=bool(a.get("agree") or a.get("verified")))
            if tid == "herbert" and (g, f) in hn:
                h_ = hn[(g, f)]
                note = dict(kind=h_["category"], label="Copied" if h_["category"] == "copied" else "Copied and re-glossed",
                            text=h_["text"], compare=None, checked=True)
            if note and note["text"]:
                e["note"] = note
            entries.append(e)
        interpolate(entries, pages)
        idv = ident.get(c["ident"]) if c.get("ident") else None
        idn = None
        if idv:
            i_ = idv["ident"]
            idn = dict(status=i_["status"], path=[h[0].replace(" [single witness]", "") for h in i_["hierarchy"]],
                       support=[h[1] for h in i_["hierarchy"]], concepts=i_["n_concepts"],
                       excluded=idv.get("excluded", []),
                       leading=i_.get("leading"),
                       candidates=[dict(name=k["name"], db=k["source"], family=(k["path"] or [""])[0],
                                        path=k["path"][:4], z=k["z"], n=k["n"]) for k in i_["candidates"][:8]],
                       evidence=[dict(concept=e_["concept"].lower(), form=e_["form"], ref=e_["ref"], d=e_["dist"])
                                 for e_ in (i_["candidates"][0].get("evidence") or [])[:12]] if i_["candidates"] else [])
        fam = glottolog.path_names(c["glotto"]) if c.get("glotto") else []
        m = md.get(c["tcp"], {})
        notes_n = sum(1 for e in entries if e.get("note"))
        rec = dict(
            schema=SCHEMA_VERSION, id=tid, wtl=f"WTL-{list(T).index(tid) + 1:04d}",
            heading=c["heading"] if "heading" in c else (heads[0] if heads else None), headings=heads[:12],
            language=dict(name=c["lang"], glottocode=c.get("glotto"), family=fam[0] if fam and fam[0] != c.get("glotto") else None,
                          path=fam[:-1] if len(fam) > 1 else [], labels=sorted(labels)),
            region=c["region"],
            book=dict(short=c["short"], title=m.get("title"), author=c["author"], printed=c["printed"],
                      imprint=m.get("date"), tcp=c["tcp"], cover=c["cover"]),
            provenance=dict(collector=c["collector"], place=c["place"], heard=c["heard"]),
            scan=dict(ia=scan["ia"], url=f"https://archive.org/details/{scan['ia']}", holder=scan.get("contributor"),
                      note=scan.get("scan_note") or None, rights="Public domain scan; image via Internet Archive"),
            pages=pages, entries=entries, identification=idn,
            stats=dict(entries=len(entries), notes=notes_n, located=sum(1 for e in entries if e.get("box"))),
            partial=c.get("partial"), relation=c.get("relation"))
        json.dump(rec, open(f"{OUT}/tables/{tid}.json", "w"), ensure_ascii=False, indent=1)
        catalog.append(dict(id=tid, wtl=rec["wtl"], heading=rec["heading"] or "", language=c["lang"], family=rec["language"]["family"],
                            region=c["region"], short=c["short"], author=c["author"], collector=c["collector"],
                            printed=c["printed"], heard=c["heard"], entries=len(entries), notes=notes_n, cover=c["cover"],
                            relation=c.get("relation"), partial=bool(c.get("partial")),
                            status=idn["status"] if idn else None))
        for e in entries:
            search.append([tid, e["n"], e["form"], e["gloss"], fold(e["form"]), fold(e["gloss"]), ",".join(e.get("concepts", []))])
    catalog.sort(key=lambda r: r["printed"])
    json.dump(catalog, open(f"{OUT}/catalog.json", "w"), ensure_ascii=False, indent=1)
    json.dump(dict(v=1, fields=["table", "n", "form", "gloss", "formFold", "glossFold", "concepts"], rows=search),
              open("site/public/data/search.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(len(catalog), "tables;", len(search), "entries;", sum(r["notes"] for r in catalog), "notes")


if __name__ == "__main__":
    main()
