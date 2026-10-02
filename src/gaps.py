"""Gap list: languages whose documentation is thinnest, as targets for archival search.

From Glottolog CLDF: languages that are extinct or nearly extinct (AES) and whose most extensive
description is a wordlist or less (MED), with their reference count, region and country. Countries
are mapped to the colonial powers whose archives are most likely to hold early records.

Output: data/work/gaps.csv
"""
import csv
import collections

B = "data/raw/glottolog_cldf/cldf/"
# country (ISO2) -> archives likely to hold pre-1900 records. Rough, by dominant early colonial power.
POWER = {
    **dict.fromkeys("MX GT HN SV NI CR PA CO VE EC PE BO CL AR PY UY CU DO PR PH".split(), "Spain"),
    **dict.fromkeys("BR AO MZ GW CV ST TL".split(), "Portugal"),
    **dict.fromkeys("ID SR ZA TW".split(), "Netherlands"),
    **dict.fromkeys("AU NZ IN MM MY SG LK GY BZ JM TT NG GH SL GM KE UG TZ ZM ZW MW BW".split(), "Britain"),
    **dict.fromkeys("GF HT SN ML GN CI BJ BF NE TD CF CG GA CM MG DZ TN VN LA KH NC PF VU".split(), "France"),
    "US": "Britain/Spain/France", "CA": "Britain/France",
}

med = {}
aes = {}
nref = {}
for r in csv.DictReader(open(B + "values.csv", encoding="utf-8")):
    p = r["Parameter_ID"]
    if p == "med":
        med[r["Language_ID"]] = int(r["Value"])
    elif p == "aes":
        aes[r["Language_ID"]] = int(r["Value"])
    elif p == "bib":
        nref[r["Language_ID"]] = len(set((r["Source"] or "").split(";")) - {""})
MEDN = {0: "long grammar", 1: "grammar", 2: "grammar sketch", 3: "phonology/text/dictionary", 4: "wordlist or less"}
AESN = {1: "not endangered", 2: "threatened", 3: "shifting", 4: "moribund", 5: "nearly extinct", 6: "extinct"}

rows = []
for r in csv.DictReader(open(B + "languages.csv", encoding="utf-8")):
    g = r["ID"]
    if r["Level"] != "language" or aes.get(g, 0) < 5 or med.get(g) != 4:
        continue
    countries = (r["Countries"] or "").split(";")
    rows.append(dict(
        glottocode=g, name=r["Name"], aes=AESN[aes[g]], med=MEDN[med[g]], n_refs=nref.get(g, 0),
        macroarea=r["Macroarea"], countries=" ".join(countries),
        power=" / ".join(sorted({POWER.get(c, "") for c in countries} - {""})),
        first_doc=r["First_Year_Of_Documentation"], last_doc=r["Last_Year_Of_Documentation"],
        family=r["Family_ID"], lat=r["Latitude"], lon=r["Longitude"]))
rows.sort(key=lambda x: (x["n_refs"], x["name"]))
with open("data/work/gaps.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(len(rows), "languages: extinct/nearly extinct with wordlist-or-less documentation")
print(collections.Counter(r["macroarea"] for r in rows).most_common())
print(collections.Counter(r["power"] or "?" for r in rows).most_common(12))
print("with <=3 refs:", sum(r["n_refs"] <= 3 for r in rows))
