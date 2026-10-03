"""Register of vocabularies, dictionaries and grammars mentioned in the VOC archive (GLOBALISE v2).

Searches the full-text index built in Historical Mysteries/globalise-drugs (read-only) for words
naming linguistic works, keeps a context window around each hit, drops hits that are plainly about
European-language books (inventories of Hoogstraten, Halma, legal dictionaries...), and collapses
duplicate copies of the same passage (the VOC series often holds two copies of a letter).

Output: data/work/voc_register/hits.jsonl
"""
import json
import re
import sqlite3

DB = "/Users/benbreen/Code/Historical Mysteries/globalise-drugs/data/voc.sqlite"
OUT = "data/work/voc_register/hits.jsonl"
QUERIES = ["vocabula*", "woordenb*", "woordb*", "woordeb*", "dictionar*", "lexicon*", "spraakk*",
           "spraeckk*", "spraeckon*", "spraekk*", "spraakon*", "grammatic*", "NEAR(lijst woorden, 3)",
           "NEAR(compendium tale, 10)", "NEAR(compendium taal, 10)"]
TERM = re.compile(r"(vocabula|woorden ?b|woordb|woordeb|dictionar|lexicon|spra+e?c?k+o?n|spraakk|spraekk|"
                  r"grammatic)\w*|lijst van (?:\w+ ){0,3}woorden|compendium(?=.{0,80}ta[ae]l)", re.I)
EUROPEAN = re.compile(r"hoogstra|halma|marin\b|pitisc|regtsgel|rechtsgel|encyclop|chomel|sewel|"
                      r"latijn|latyn|lat\.? et belg|fransch|franse|engelsch|hoogduits|hebr|grieks|"
                      r"italiaan|spaans", re.I)
NONEURO = re.compile(r"mal[ae][iy]|malabaa?r|tamul|singal|cingal|hottento|madagas|formos|sinees|chinees|"
                     r"japan|javaan|bougi|boegi|macas|amboin|ulias|persia|perzia|arab|mooren|bengaal|"
                     r"portugees|siam|pegu|ternat|bandas|timor|sumatra|tale|taal|spraak|spraeck", re.I)


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def main():
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    seen_pages, seen_ctx, n_raw, n_euro = set(), set(), 0, 0
    out = open(OUT, "w", encoding="utf-8")
    kept = 0
    for q in QUERIES:
        for pid, sid, inv, seq, text in db.execute(
                "select p.id, p.scan_id, p.inventory, p.sequence, p.text from pages_fts "
                "join pages p on p.id = pages_fts.rowid where pages_fts match ?", (q,)):
            if pid in seen_pages:
                continue
            seen_pages.add(pid)
            flat = text.replace("\n", " ")
            for m in TERM.finditer(flat):
                n_raw += 1
                ctx = flat[max(0, m.start() - 700):m.end() + 500]
                near = flat[max(0, m.start() - 150):m.end() + 150]
                if EUROPEAN.search(near) and not NONEURO.search(near):
                    n_euro += 1
                    continue
                key = norm(flat[max(0, m.start() - 120):m.end() + 120])[:160]
                # near-duplicate copies: same 60-char core around the term
                core = norm(flat[max(0, m.start() - 60):m.end() + 60])
                if key in seen_ctx or core in seen_ctx:
                    continue
                seen_ctx.update({key, core})
                kept += 1
                out.write(json.dumps(dict(id=kept, scan=sid, inventory=inv, seq=seq, term=m.group(),
                                          context=ctx), ensure_ascii=False) + "\n")
    print(f"{len(seen_pages)} pages, {n_raw} term hits, {n_euro} European-only dropped, {kept} kept")


if __name__ == "__main__":
    main()
