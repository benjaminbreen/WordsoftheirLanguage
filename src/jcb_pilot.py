"""JCB pilot: look for embedded vocabularies in John Carter Brown Library scans on the Internet Archive.

EEBO stops at 1700 and is English only. The JCB's digitised books run to 1900 and are mostly
Spanish, Portuguese, French, Latin and Dutch. This script:
  1. lists JCB texts with travel / mission / Indian subject headings (excluding the
     `jcbindigenous` collection, which is already catalogued linguistic material);
  2. downloads each book's OCR plain text (`_djvu.txt`);
  3. scores pages for word-list structure in any of seven European gloss languages.

The OCR is noisy (long s read as f, broken words), so "rare" here means: a token that appears in
few books of this corpus AND is not junk (letters only, 3-14 chars, at least one vowel). Two signals:
  - pair lines: short OCR lines holding one gloss word and one rare word (the shape of a table);
  - window events: as in detect.py, distinct rare forms within K tokens of distinct glosses.

Usage:  python src/jcb_pilot.py list | fetch | scan
Output: data/work/jcb/{items.json, txt/, candidates.csv}
"""
import collections
import csv
import json
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor

import requests

W = "data/work/jcb"
TXT = f"{W}/txt"

QUERY = ("collection:JohnCarterBrownLibrary AND mediatype:texts AND NOT collection:jcbindigenous "
         "AND subject:(travel OR voyages OR description OR indians OR missions)")
# Books whose tables are already on the site: recall controls.
CONTROLS = ["keyintolanguageo02will", "newenglandsprosp01wood", "mapofvirginiavvi00smit",
            "shortebriefenarr00cart", "historyofcaribby00roch", "voyagestravellso00olea",
            "historicalgeogra01thom", "americabeinglate01mont"]

GLOSS_WORDS = {
    "eng": """head haire eye eyes nose mouth teeth tongue eare hand hands foot feete belly heart man woman
        wife father mother brother sister sonne daughter child sunne moone starre heauen raine winde fire
        water sea riuer earth stone tree day night house towne canoe bowe arrow knife hatchet bread fish
        flesh deere dogge bird corne tobacco come goe eate drinke sleepe good great little white black red
        one two three foure fiue sixe seuen eight nine ten twenty hundred yes""",
    "spa": """cabeça cabeza cabello ojo ojos nariz boca diente dientes lengua oreja mano manos pie pies
        vientre coraçon corazon hombre muger mujer padre madre hermano hermana hijo hija niño sol luna
        estrella cielo lluvia viento fuego agua mar rio tierra piedra arbol dia noche casa pueblo canoa
        arco flecha cuchillo hacha pan pescado carne venado perro pajaro maiz tabaco venir ir comer beber
        dormir bueno grande pequeño blanco negro colorado uno dos tres quatro cuatro cinco seis siete ocho
        nueve diez veinte ciento si""",
    "por": """cabeça cabello cabelo olho olhos nariz boca dente dentes lingua orelha mão mãos pé pés barriga
        coração homem mulher pai mãy mãe irmão irmã filho filha menino sol lua estrella estrela ceo céu chuva
        vento fogo agoa agua mar rio terra pedra arvore dia noite casa aldea canoa arco flecha frecha faca
        machado pão peixe carne veado cão passaro milho tabaco vir ir comer beber dormir bom grande pequeno
        branco preto vermelho hum huma dous duas tres quatro cinco seis sete oito nove dez vinte cem sim""",
    "fre": """teste tête cheveux oeil yeux nez bouche dent dents langue oreille main mains pied pieds ventre
        coeur homme femme pere père mere mère frere frère soeur fils fille enfant soleil lune estoile étoile
        ciel pluye pluie vent feu eau mer riviere terre pierre arbre jour nuit maison village canot arc
        fleche flèche couteau hache pain poisson chair viande cerf chien oiseau bled tabac venir aller
        manger boire dormir bon grand petit blanc noir rouge un deux trois quatre cinq six sept huit neuf
        dix vingt cent oüy oui""",
    "dut": """hooft hoofd hayr hair oogh oogen neus mondt mond tant tanden tonge oor handt hand voet voeten
        buyck hert man vrouw wijf vader moeder broeder suster soon dochter kint son maen sterre hemel regen
        wint vuur vier water zee rivier aerde steen boom dagh nacht huys dorp canoe boogh pijl mes bijl
        broot visch vleesch hert hondt vogel mays tabak komen gaen eten drincken slapen goet groot kleyn
        wit swart root een twee drie vier vijf ses seven acht negen thien twintigh hondert ja""",
    "lat": """caput capillus oculus oculi nasus os dens dentes lingua auris manus pes pedes venter cor homo
        vir mulier femina uxor pater mater frater soror filius filia puer sol luna stella coelum caelum
        pluvia ventus ignis aqua mare flumen fluvius terra lapis arbor dies nox domus pagus arcus sagitta
        culter securis panis piscis caro cervus canis avis bonus magnus parvus albus niger ruber unus duo
        tres quatuor quinque sex septem octo novem decem viginti centum""",
    "ger": """kopf kopff haar aug augen nase mund zahn zähne zung ohr hand fuss fuß bauch hertz mann weib
        frau vater mutter bruder schwester sohn tochter kind sonne mond stern himmel regen wind feuer
        wasser meer fluss erde stein baum tag nacht haus dorff bogen pfeil messer beil brodt brot fisch
        fleisch hirsch hund vogel tabac kommen gehen essen trincken schlaffen gut groß gross klein weiß
        schwartz roth eins zwey drey vier fünff sechs sieben acht neun zehen zwantzig hundert ja""",
}


def fold(s):
    """Fold OCR and early-modern variation: long s / f, u/v, i/j/y, accents."""
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if c.isalpha())
    for a, b in (("ſ", "s"), ("f", "s"), ("v", "u"), ("j", "i"), ("y", "i"), ("w", "uu"), ("ph", "f")):
        s = s.replace(a, b)
    return s


GLOSS = {}
for lang, ws in GLOSS_WORDS.items():
    for w in ws.split():
        GLOSS.setdefault(fold(w), set()).add(lang)

TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)?")
VOWEL = re.compile(r"[aeiouyáéíóúàèìòùâêîôûãõäëïöü]", re.I)


def list_items():
    os.makedirs(W, exist_ok=True)
    docs, page = [], 1
    while True:
        r = requests.get("https://archive.org/advancedsearch.php", params={
            "q": QUERY, "fl[]": ["identifier", "title", "date", "language", "subject"],
            "rows": 500, "page": page, "output": "json"}, timeout=120).json()["response"]
        docs += r["docs"]
        if len(docs) >= r["numFound"] or not r["docs"]:
            break
        page += 1
    have = {d["identifier"] for d in docs}
    for c in CONTROLS:
        if c not in have:
            docs.append({"identifier": c, "control": True})
    for d in docs:
        d["control"] = d["identifier"] in CONTROLS
    json.dump(docs, open(f"{W}/items.json", "w"), indent=0)
    print(len(docs), "items")


def fetch_one(ia):
    p = f"{TXT}/{ia}.txt"
    if os.path.exists(p):
        return True
    try:
        r = requests.get(f"https://archive.org/download/{ia}/{ia}_djvu.txt", timeout=180)
        if r.status_code != 200:
            return False
        open(p, "w", encoding="utf-8").write(r.text)
        return True
    except requests.RequestException:
        return False


def fetch():
    os.makedirs(TXT, exist_ok=True)
    items = json.load(open(f"{W}/items.json"))
    with ThreadPoolExecutor(12) as ex:
        ok = list(ex.map(fetch_one, [d["identifier"] for d in items]))
    print(sum(ok), "of", len(ok), "texts fetched")


def clean_token(t):
    f = fold(t)
    return f if 3 <= len(f) <= 14 and VOWEL.search(f) else None


def scan():
    items = {d["identifier"]: d for d in json.load(open(f"{W}/items.json"))}
    texts = {}
    for ia in items:
        p = f"{TXT}/{ia}.txt"
        if os.path.exists(p):
            texts[ia] = open(p, encoding="utf-8").read()
    # document frequency over this corpus
    df = collections.Counter()
    for t in texts.values():
        df.update({f for f in map(fold, TOKEN_RE.findall(t)) if f})
    n = len(texts)
    rare_max = max(2, n // 200)  # in <= 0.5% of books

    def is_rare(f):
        return f and f not in GLOSS and df[f] <= rare_max

    rows = []
    for ia, text in texts.items():
        # IA djvu.txt separates pages with form feeds; fall back to ~3000-char chunks
        pages = text.split("\f") if "\f" in text else [text[i:i + 3000] for i in range(0, len(text), 3000)]
        for pi, pg in enumerate(pages):
            pair_lines, rares, glosses, langs = 0, set(), set(), collections.Counter()
            for line in pg.splitlines():
                toks = [clean_token(t) for t in TOKEN_RE.findall(line)]
                toks = [t for t in toks if t]
                if not 2 <= len(toks) <= 6:
                    continue
                g = [t for t in toks if t in GLOSS]
                r = [t for t in toks if is_rare(t)]
                if g and r:
                    pair_lines += 1
                    rares.update(r)
                    glosses.update(g)
                    for t in g:
                        langs.update(GLOSS[t])
            score = min(len(rares), len(glosses))
            if pair_lines >= 5 and score >= 4:
                d = items[ia]
                rows.append(dict(
                    ia=ia, page=pi, score=score, pair_lines=pair_lines,
                    gloss_lang=langs.most_common(1)[0][0] if langs else "",
                    control=d.get("control", False), date=str(d.get("date", ""))[:4],
                    language=",".join(d["language"]) if isinstance(d.get("language"), list) else d.get("language", ""),
                    title=(d.get("title") or "")[:120],
                    rare_sample=" ".join(sorted(rares)[:25]), gloss_sample=" ".join(sorted(glosses)[:25]),
                ))
    rows.sort(key=lambda r: (-r["score"], -r["pair_lines"]))
    with open(f"{W}/candidates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    books = {r["ia"] for r in rows}
    ctrl = [c for c in CONTROLS if c in texts]
    hit = [c for c in ctrl if c in books]
    print(f"{n} books scanned; {len(rows)} candidate pages in {len(books)} books")
    print(f"control recall: {len(hit)}/{len(ctrl)}; missed: {sorted(set(ctrl) - set(hit))}")


if __name__ == "__main__":
    {"list": list_items, "fetch": fetch, "scan": scan}[sys.argv[1]]()
