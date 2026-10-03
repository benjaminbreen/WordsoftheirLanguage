"""Merge agent classifications of VOC register hits into one row per work.

Input:  data/work/voc_register/classified_*.jsonl
Output: data/work/voc_register/register.csv (one row per work) and register_hits.csv
"""
import collections
import csv
import glob
import json

# agent work_key -> canonical work id. Keys absent here map to themselves; None drops them.
CANON = {
    "cat-sinhala-dutch-dictionary-colombo-1694": "cat-sinhala-dictionary",
    "cat-dutch-sinhala-dictionary-1694": "cat-sinhala-dictionary",
    "kat-dutch-sinhala-dictionary-ceylon-1690s": "cat-sinhala-dictionary",
    "cat-multilingual-lexicon-ceylon": "cat-sinhala-dictionary",
    "cat-dutch-sinhala-grammar-colombo-1690s": "borgim-cat-sinhala-grammar",
    "borgan-sinhala-grammar-1645": "borgim-cat-sinhala-grammar",
    "borgim-sinhala-grammar-1645": "borgim-cat-sinhala-grammar",
    "sinhala-grammar-ms-~1700": "borgim-cat-sinhala-grammar",
    "singhalese-dictionary-colombo-1750s": "colombo-sinhala-dictionary-1750s",
    "singhalese-dictionary-colombo-press-1750s": "colombo-sinhala-dictionary-1750s",
    "sinhala-dictionary-colombo-1750s": "colombo-sinhala-dictionary-1750s",
    "sinhala-dictionary-printing-colombo-1750s": "colombo-sinhala-dictionary-1750s",
    "colombo-library-inventory-1757-sinhala-dictionaries": "colombo-sinhala-dictionary-1750s",
    "colombo-church-dictionary-inventory-1757": "colombo-sinhala-dictionary-1750s",
    "ruell-sinhala-grammar-1708": "ruell-sinhala-grammar",
    "tamil-dutch-dictionary-jaffna-1690": "jaffna-tamil-dictionary",
    "tamil-dutch-dictionary-jaffna-1710s": "jaffna-tamil-dictionary",
    "dutch-tamil-woordenboek-jaffna-devooght-demeij": "jaffna-tamil-dictionary",
    "jaffna-dutch-tamil-school-vocabulary-1690s": "jaffna-tamil-dictionary",
    "devoogt-tamil-vocabulary-1670s": "jaffna-tamil-dictionary",
    "jaffna-tamil-grammar-1720s": "jaffna-tamil-grammar",
    "jaffna-tamil-grammar-dictionary-1710s": "jaffna-tamil-grammar",
    "jaffna-tamil-grammar-dictionary-1716": "jaffna-tamil-grammar",
    "kramer-tamil-dictionary-enclosure-1716": "kramer-teacher-tamil-wordlist",
    "kramer-tamil-wordlist-1720s": "kramer-teacher-tamil-wordlist",
    "kramer-tamil-dictionary-from-tiwagaram": "kramer-teacher-tamil-wordlist",
    "tivakaram-tamil-nighantu": "tivakaram", "tivakaram-tamil-lexicon": "tivakaram",
    "tamil-nighantu-agarathi": "tivakaram", "akarathi-nigandu-tamil": "tivakaram",
    "malabar-woordeboek-vangollenesse-1743": "vangollenesse-malabar-dictionary-1743",
    "malabar-woordenboek-gollenesse-memorie-1743": "vangollenesse-malabar-dictionary-1743",
    "van-gollenesse-memorie-tamil-dictionary-1743": "vangollenesse-malabar-dictionary-1743",
    "elbracht-persian-grammar-bengal-1778": "elbracht-persian-grammar-1778",
    "werndly-malay-dictionary-1730s": "werndly-malay-grammar-1736",
    "ternate-request-sihah-qamus-1745": "arabic-sihah-qamus-request-sultan",
    "flacourt-malagasy-dictionary-1658": "flacourt-malagasy-dictionary-1658",
    # generic, European scholarly, or not a specific work
    **dict.fromkeys(["booklist-1278-arabic-syriac-grammars", "booklist-1278-armenian-dictionary",
                     "booklist-1278-chaldaic-lexicon", "colombo-seminary-grammar-teaching",
                     "generic-language-aids-ceylon-1760", "printing-type-request-grammar-dictionary",
                     "schoolmasters-confiscated-books-woordeboek-1690s", "halma-vocabulary-1680s",
                     "erpenius-arabic-grammar", "castell-golius-persian-lexicon",
                     "latin-arabic-dictionary-request-1650s", "catholic-missionary-grammars-dictionaries",
                     "malay-grammar-stock-1740s", "malay-dictionary-printed-batavia-18c",
                     "malay-dutch-dictionary-amsterdam-schoolbooks", "malabar-gazetteer-woordeboek"], None),
}


def main():
    hits = [json.loads(l) for p in sorted(glob.glob("data/work/voc_register/classified_*.jsonl")) for l in open(p)]
    hits = [h for h in hits if h.get("relevant")]
    groups = collections.defaultdict(list)
    for h in hits:
        k = CANON.get(h["work_key"], h["work_key"])
        if k:
            h["work"] = k
            groups[k].append(h)
    rows = []
    for k, hs in groups.items():
        def top(f):
            c = collections.Counter(str(h.get(f) or "").strip() for h in hs) - collections.Counter({"": 10**6})
            return c.most_common(1)[0][0] if c else ""
        status = sorted({h.get("status_in_text") or "" for h in hs} - {""})
        years = sorted({str(h.get("year")) for h in hs if h.get("year")})
        rows.append(dict(work=k, n_mentions=len(hs), language=top("language"), modern_id=top("modern_id"),
                         kind=top("kind"), compiler=top("compiler"), place=top("place"),
                         years=" ".join(years[:6]), statuses="; ".join(status),
                         copy_in_archive=any("copy" in s for s in status),
                         scans=" ".join(sorted({h["scan"] for h in hs})[:12]),
                         note=max((h.get("note") or "" for h in hs), key=len)))
    rows.sort(key=lambda r: -r["n_mentions"])
    with open("data/work/voc_register/register.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(hits), "relevant hits ->", sum(len(v) for v in groups.values()), "kept in", len(rows), "works")


if __name__ == "__main__":
    main()
