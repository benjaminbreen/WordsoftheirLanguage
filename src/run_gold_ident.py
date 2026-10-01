import sys, json
import identify2 as I
ref = I.Reference()
cases = [a.split(":", 2) for a in sys.argv[1:]]
for name, prof, excl in cases:
    res = I.identify(I.read_entries(f"data/work/extract/{name}.entries.csv"), ref,
                     set(x for x in excl.split("+") if x), prof)
    json.dump(res, open(f"out/ident/{name}.json", "w"), ensure_ascii=False, indent=1)
    print(f"##### {name}: {res['n_entries']} entries, {res['n_concepts']} concepts, affixes {res['affixes_removed']}")
    for t in res["candidates"][:8]:
        print(f"  {'*' if t['p'] <= I.ALPHA else ' '} ldnd={t['ldnd']:.3f} n={t['n']:3d} p={t['p']:.3f} z={t['z']:5.2f} {t['source']:8} {t['name'][:30]:30} {' > '.join(t['path'][:3])[:60]}")
    print("  STATUS:", res["status"], "|", " > ".join(f"{n} ({s})" for n, s in res["hierarchy"]))
