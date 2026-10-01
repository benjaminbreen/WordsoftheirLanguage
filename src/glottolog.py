"""Glottolog ancestor paths (root family -> ... -> languoid) from glottolog-cldf Newick trees."""
import csv
import functools
import re

BASE = "data/raw/glottolog_cldf/cldf/"


@functools.lru_cache(maxsize=1)
def load():
    names, level = {}, {}
    for r in csv.DictReader(open(BASE + "languages.csv", encoding="utf-8")):
        names[r["ID"]] = r["Name"]
        level[r["ID"]] = r["Level"]
    paths = {}
    for r in csv.DictReader(open(BASE + "values.csv", encoding="utf-8")):
        if r["Parameter_ID"] != "subclassification":
            continue
        _parse(r["Value"], paths)
    # isolates and unclassified: path is just themselves
    for g in names:
        paths.setdefault(g, [g])
    return names, level, paths


def _parse(newick, paths):
    """Walk Newick; each node label is 'code:1'. Record path from root to every node."""
    s = newick.strip().rstrip(";")
    stack = [[]]          # children-label lists per open paren
    # simple tokenizer: we need the label that follows each ')' and plain leaf labels
    tokens = re.findall(r"\(|\)|,|[a-z0-9]{4}\d{4}(?::[\d.]+)?", s)
    # Build tree via recursive descent
    pos = 0

    def node():
        nonlocal pos
        children = []
        if tokens[pos] == "(":
            pos += 1
            children.append(node())
            while tokens[pos] == ",":
                pos += 1
                children.append(node())
            assert tokens[pos] == ")"
            pos += 1
        label = tokens[pos].split(":")[0] if pos < len(tokens) and tokens[pos] not in "(),"else None
        if label:
            pos += 1
        return (label, children)

    root = node()

    def walk(n, prefix):
        label, ch = n
        p = prefix + [label] if label else prefix
        if label and len(p) > len(paths.get(label, [])):
            paths[label] = p
        for c in ch:
            walk(c, p)

    walk(root, [])


def path_names(glottocode):
    names, level, paths = load()
    return [names.get(g, g) for g in paths.get(glottocode, [glottocode])]


def family(glottocode):
    names, level, paths = load()
    p = paths.get(glottocode, [glottocode])
    return names.get(p[0], p[0])
