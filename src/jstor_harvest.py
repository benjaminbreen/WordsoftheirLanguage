"""Harvest candidate word-list articles from JSTOR Early Journal Content (Internet Archive collection jstor_ejc).

Title search (metadata) and full-text phrase search; dedupe; drop items already triaged or on the site.
Output: data/work/jstor2/candidates.jsonl
"""
import json
import time

import requests

UA = {"User-Agent": "WordesOfTheirLanguage research (bebreen)"}
TITLE_TERMS = ["vocabulary", "vocabularies", "words", "word", "language", "languages", "dialect", "dialects",
               "numerals", "glossary", "specimen", "specimens", "tongue", "lexicon", "grammar"]
FT_PHRASES = ["vocabulary of the", "list of words", "words of the language", "words in the language",
              "numerals of the", "specimen of the language", "a few words of", "short vocabulary",
              "comparative vocabulary", "vocabulary of words"]


def title_search():
    out = {}
    for t in TITLE_TERMS:
        page = 1
        while True:
            r = requests.get("https://archive.org/advancedsearch.php", headers=UA, timeout=120, params={
                "q": f"collection:jstor_ejc AND title:({t}) AND year:[1665 TO 1923]",
                "fl[]": ["identifier", "title", "year", "creator", "source", "publisher"],
                "rows": 1000, "page": page, "output": "json"}).json()["response"]
            for d in r["docs"]:
                out.setdefault(d["identifier"], dict(d, how=set()))["how"].add("title:" + t)
            if page * 1000 >= r["numFound"] or not r["docs"]:
                break
            page += 1
            time.sleep(1)
    return out


def fulltext(out):
    for ph in FT_PHRASES:
        for y0, y1 in ((1665, 1800), (1801, 1850), (1851, 1880), (1881, 1923)):
            try:
                r = requests.get("https://archive.org/services/search/beta/page_production/", headers=UA, timeout=120, params={
                    "user_query": f'"{ph}" AND collection:jstor_ejc AND year:[{y0} TO {y1}]', "service_backend": "fts",
                    "page_type": "collection_details", "page_target": "texts", "hits_per_page": 100}).json()
            except Exception as e:
                print("fts fail", ph, y0, e)
                continue
            hits = (r.get("response", {}).get("body", {}).get("hits", {}) or {}).get("hits", [])
            for h in hits:
                f = h.get("fields", {})
                ident = f.get("identifier")
                if not ident:
                    continue
                d = out.setdefault(ident, dict(identifier=ident, title=f.get("title"), year=f.get("year"),
                                               creator=f.get("creator"), how=set()))
                d["how"].add("ft:" + ph)
                hl = h.get("highlight", {}).get("text") or []
                if hl:
                    d.setdefault("snippets", []).extend(hl[:2])
            time.sleep(1)
    return out


if __name__ == "__main__":
    out = fulltext(title_search())
    with open("data/work/jstor2/candidates.jsonl", "w") as f:
        for d in out.values():
            d["how"] = sorted(d["how"])
            f.write(json.dumps(d, ensure_ascii=False, default=str) + "\n")
    print(len(out), "candidates")
