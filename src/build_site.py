"""Render out/site/index.html from site/template.html + out/site/data.json + findings."""
import json

import identify2 as I

FINDINGS = [
    dict(kind="New finding · transmission",
         title="Thomas Herbert's 'Malayan Tongue' (1634) is a re-sorted copy of the 1601 English van Neck vocabulary",
         body="The lineage detector linked Herbert's travel book to the English translation of Jacob van Neck's journal through 76 shared rare spellings. "
              "Entry by entry, <b>226 of Herbert's 243</b> Malay forms match van Neck's, though Herbert presents the list as part of his own 1627–29 voyage. "
              "He re-sorted van Neck's alphabetical list by topic and re-glossed it as he went, so about 70 entries keep the Malay word but carry the wrong meaning. "
              "His errors work like stemmatic markers: later Malay lists in Olearius's Mandelslo (1669) and Ogilby's <i>Asia</i> (1673) share van Neck's forms but none of Herbert's mistakes, so they reached print independently of him.",
         pairs=[["Ise", "van Neck: Gréene", "Herbert: “I see, Green” (gloss and form inverted)"],
                ["Tieda", "van Neck: No", "Herbert: “To spin”"],
                ["Ampo", "van Neck: to Forgiue", "Herbert: “To poyson”"],
                ["Apon", "van Neck: Faire", "Herbert: “A shooe”"],
                ["Gatto d'algalia", "van Neck: a Cyuet Cat", "Italian, passed on as Malay"]],
         meta="Sources: <a href='#v-vanneck'>van Neck 1601 list</a> · EEBO-TCP A03065, A03066, A08052. "
              "We found no prior statement of this in the sources we could check; John Butler's annotated editions of Herbert have not yet been consulted."),
    dict(kind="Validation",
         title="Working blind, the identifier reproduces three expert identifications made between 1895 and 1940",
         body="With labels, places and titles hidden, three lists printed without a usable language name were matched against 17,041 modern wordlists. "
              "Each result agrees with a specialist's earlier finding, down to the dialect and the morphology.",
         pairs=[["Burrough 1557", "Kildin Saami, z = 17", "Genetz 1895: “decided agreement” with Kildin"],
                ["Dudley 1595, Trinidad", "Lokono (Arawak), z = 7.8", "Warner 1899: Arawak; da- = “my”"],
                ["“Pegu language”, 1601", "Mon, z = 5.7", "Blagden, in Foster 1940: Mon (Talaing)"]],
         meta="Lists: <a href='#v-sami_burrough'>Burrough</a> · <a href='#v-trinidad'>Trinidad</a> · <a href='#v-pegu'>Pegu</a>. "
              "The Trinidad match appeared only after the system detected and set aside the recurring prefix <i>da-</i>."),
    dict(kind="Validation · leave-lineage-out",
         title="With every Island Carib wordlist removed, Rochefort's 1666 Caribbean vocabulary goes straight to Garifuna",
         body="Reference databases already contain the 17th-century Island Carib sources, so a naive test would let a list match itself. "
              "Removing them leaves Garifuna, the living descendant of Island Carib, as the top match (z = 11.9). "
              "Rosier's 1605 Maine list resolves to Eastern Algonquian › Abenaki, in line with modern discussion of it as Etchemin or Eastern Abenaki.",
         meta="<a href='#v-rochefort'>Rochefort</a> · <a href='#v-rosier'>Rosier</a> · <a href='#method'>benchmark</a>"),
    dict(kind="Research thread · elicitation",
         title="Questions recorded as words",
         body="Collectors pointed and asked; sometimes the answer they wrote down was the question. Reviewers flagged these across unrelated lists, a pattern that becomes visible only at corpus scale.",
         pairs=[["Mugaru", "“what call you it”", "Pegu list, 1601"],
                ["Sua · Suna", "“what wouldst?” · “what is't”", "Olearius's Greenlanders"],
                ["Kia mecle", "“which signifies”", "Olearius's Greenlanders"],
                ["Non quo · Non quapa", "“I know not” · “I cannot tell”", "Trinidad, 1595"],
                ["Biskeiore", "“cod-fish”", "Rosier 1605: a Basque trade word"]],
         meta="Contact and mis-elicitation flags are stored for every extracted entry."),
    dict(kind="Research thread · invention",
         title="Invented and mock languages sit in the same print culture",
         body="The detector cannot tell a vocabulary of the angels from one of the Abenaki, and that is useful. It surfaced John Dee's spirit language (1659), "
              "Joseph Hall's satirical 'Supermonicall tongue' (1613), Thomas Tany's visionary language (1655), the pseudo-Arabic footnotes of Miguel de Luna's forged "
              "<i>Almanzor</i> (1693), mock-Turkish on the Restoration stage (1672), and a 1688 'Alphabetical Dictionary of the Dumb Language' of Turkish love tokens, decades before the language of flowers became fashionable.",
         meta="<a href='#census'>Census</a> → filter “Invented or mock languages”."),
    dict(kind="Honest abstentions",
         title="Where the catalogue says it does not know",
         body="Cartier's 1535 Hochelaga list records Laurentian, which has no modern wordlist, and the system abstains instead of forcing a match. "
              "Gabriel Thomas's 1698 Pennsylvania dialogue is a trade pidgin and also abstains once the Delaware references are removed. "
              "Boothby's Madagascar list (gathered at St Augustine's Bay in 1630) resolves only to southwestern Malagasy; finer dialect claims would need Vezo data the references lack.",
         meta="<a href='#v-cartier'>Cartier</a> · <a href='#v-gthomas'>Thomas</a> · <a href='#v-boothby'>Boothby</a>"),
]

BENCH = [
    ("Rosier 1605 (Maine)", "none", "rosier", "matches literature (Eastern Algonquian / Abenaki)"),
    ("Wood 1634 (Massachusett)", "none", "wood", "correct (Wampanoag top)"),
    ("Rochefort 1666 (Island Carib)", "Island Carib, Breton 1665", "rochefort", "correct (Garifuna)"),
    ("Scheffer 1674 (Sami)", "none", "scheffer", "correct"),
    ("van Neck 1601 (Malay)", "none", "vanneck", "correct"),
    ("Boothby 1646 (Malagasy)", "none", "boothby", "correct at family and subgroup"),
    ("Knox 1681 (Sinhala)", "none", "knox", "family correct; leaf wrong (thin Sinhala data)"),
    ("Smith 1612 (Powhatan)", "Powhatan", "smith_map", "abstains; leading family correct"),
    ("Williams 1643 (Narragansett)", "Narragansett", "williams", "abstains; glosses are phrases"),
    ("Cartier 1580 (Laurentian)", "Laurentian (absent anyway)", "cartier", "abstains, as it should"),
]


def main():
    data = json.load(open("out/site/data.json"))
    data["threshold"] = I.Z_THRESHOLD
    V = {v["id"]: v for v in data["vocabularies"]}
    data["bench"] = []
    for name, excl, vid, verdict in BENCH:
        v = V[vid]
        h = v["ident"]["hierarchy"]
        res = (h[-1][0].replace(" [single witness]", "") if h else "")
        data["bench"].append(dict(name=name, excl=excl, status=v["ident"]["status"], result=res, verdict=verdict))
    data.pop("benchmark", None)
    tpl = open("site/template.html").read()
    js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__DATA__", js(data)).replace("__FINDINGS__", js(FINDINGS))
    open("out/site/index.html", "w").write(html)
    print(len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
