"""Early-modern English gloss words that tend to appear in encounter vocabularies.

Spelling variants are generated loosely (u/v, i/j/y, final -e, doubled consonants),
so the list itself stays readable. Everything is lowercase.
"""
import re

BASE = """
head hed heade haire hair heare eye eyes eie eies eyen nose mouth mouthe tooth teeth tongue tong
eare eares ear ears lip lips chin beard necke neck arme armes arm hand hands finger fingers nayle nailes
legge legges leg legs foote feete foot feet knee knees belly bellie brest breast breasts back bone bones
bloud blood skin heart hart face forehead navell thigh shoulder elbow cheeke cheekes
man men woman women wife husband childe child children boy girl father mother brother sister sonne son
daughter king captaine friend enemie enemy god devil deuill lord
sunne sun moone moon starre starres star stars skie sky heauen heaven cloud clouds raine rain winde wind
thunder lightning fire fyre water sea river riuer lake ice snow earth ground land sand stone stones
mountaine hill wood woods tree trees leafe leaues root grasse herbe
day night morning euening evening yesterday to-morrow tomorrow winter summer yeere yeare year
house houses towne village boat boate canoa canoe canow ship shippe oare paddle
bow bowe arrow arrowes arrows knife knives knyfe hatchet hatchets axe ax hammer sword swords gunne gun
pot kettle dish spoone beads beades copper iron yron brasse gold siluer silver pearle pearles glasse
corne maize maiz bread fish fishe fishes flesh meate meat deere deer beare bear dogge dog dogs foxe fox
beuer beauer beaver otter wolfe wolf bird birds fowle fowles hen goose duck egge egges turtle snake serpent
cod whale seale tobacco tabacco tobaco pipe skinne skins furre furres mat mats
come go goe sit sleepe sleep eat eate drinke drink giue give see heare speake run dance kill laugh weepe
good bad great little small hot cold white black red greene yellow
yes no not
one two three foure four fiue five sixe six seuen seven eight nine ten eleuen twelue twenty hundred
"""

BASE_SET = set(BASE.split())


def _variants(w: str) -> set[str]:
    out = {w}
    swaps = [("v", "u"), ("u", "v"), ("i", "y"), ("y", "i"), ("j", "i")]
    for a, b in swaps:
        if a in w:
            out.add(w.replace(a, b))
    more = set()
    for x in out:
        more.add(x + "e" if not x.endswith("e") else x[:-1])
        more.add(x + "s")
    out |= more
    return {x for x in out if len(x) > 1}


GLOSSES: frozenset[str] = frozenset(v for w in BASE_SET for v in _variants(w))

# Common English function words. Gloss words that collide with these are ok.
STOP = frozenset("""
the and of to in a is that it for his he which with as be by this they their them not are was
or on all but from have so at we an i you my shall will thy thee our do me him her one there
are they were what when then than who whom whose these those such also into vpon upon unto
""".split())

HEADING_RE = re.compile(
    r"(?i)\b(vocabular\w*|dictionar\w*|words?\s+(?:of|in|vsed|used|which)\b|"
    r"(?:their|the\w*)\s+(?:language|langu\w+|tongue|speech)|"
    r"language\s+of|tongue\s+of|names?\s+of\s+(?:things|their))"
)

# "which they call X", "called in their language X", "X, which signifieth"
CALL_RE = re.compile(
    r"(?i)\b(?:they\s+call(?:ed)?|is\s+called|are\s+called|call(?:ed)?\s+it|"
    r"in\s+their\s+(?:language|tongue|speech)|(?:doth\s+)?signif(?:ie|y)\w*|which\s+is\s+to\s+say)\b"
)

TOKEN_RE = re.compile(r"[A-Za-zÀ-ÿĀ-ſ']+")
