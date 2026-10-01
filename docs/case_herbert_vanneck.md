# Case study: Thomas Herbert's "Malayan Tongue" (1634) is a re-sorted copy of the 1601 English van Neck vocabulary

Status: **strong evidence of derivation; novelty check against Herbert scholarship pending** (see `novelty_check.md`).

## How it surfaced

The transmission-network step (`src/lineage2.py`) links books that share rare foreign spellings found
inside confirmed vocabulary windows. Among links between *different authors* that are not acknowledged
compilations (Hakluyt, Purchas), the strongest is:

| Book | Year | Shared rare spellings |
|---|---|---|
| Herbert, *A relation of some yeares trauaile* (EEBO-TCP A03065) ↔ van Neck, *The iournall, or dayly register* (A08052) | 1634 ↔ 1601 | 76 |
| Herbert, *Some yeares travels* 2nd ed. (A03066) ↔ van Neck (A08052) | 1638 ↔ 1601 | 63 |

Herbert presents the list ("I will insert some words of the *Malayan* Tongue spoken in many Ilands of the
Orient") inside the narrative of his own 1627-29 voyage, without naming a source.

## Entry-level alignment

`out/cases/herbert_vs_vanneck_alignment.csv` aligns Herbert's 243 entries (Malay list + Javanese list +
numerals) against the 299 entries of the van Neck English list (extracted in `data/work/extract/vanneck_A08052.entries.csv`).

- **226 / 243** Herbert forms match a van Neck form at fuzzy similarity ≥ 80 (after folding u/v, i/j/y).
- Most of the remaining 17 are visible misreadings of van Neck forms (*Maety pooty* → *Marty-lowty*,
  *Addollaley* → *Addal-ally*, *Iaryiary* → *Iary-laree*, *Caiu Lacca* → *Caju-••cta*).
- **~70 entries keep van Neck's form but attach a different English meaning.** Herbert re-sorted van Neck's
  alphabetical list into semantic groups (kin, animals, trade goods, body, verbs) and re-glossed as he went.

### Diagnostic errors (only explicable by copying the printed English text)

| van Neck 1601 (English) | Herbert 1634 | Mechanism |
|---|---|---|
| Gréene – *Ise* | I see, *Green* | gloss and form **inverted**: "Gréene" taken as the Malay word, *Ise* read as English "I see" |
| Is there – *Beeff* | Is he not here *Bees* | *ff* / long-s misread |
| Ours – *Quitabota* | To vs, *Quia bota* | |
| a Swéetcheart – *Nay moeda* | A Booke, *Naymoda* | form moved to wrong gloss |
| Faire – *Apon* | A shooe, *Apon* | |
| Feare – *Tacat* | Fruit, *Tacat* | |
| NO – *Tieda* | To spin, *Tyeda* | the Malay negator *tidak* becomes "to spin" |
| to Forgiue – *Ampo* | To poyson, *Ampo* | (Malay *ampun* 'pardon') |
| Blacke – *Ita* | A Sword, *Ita* | (Malay *hitam* 'black') |
| the Cough – *Capello* | A Ship, *Capell* | |
| FOlly – *Bengo* | Mace, *Bengo* | |
| POore – *Backeyen* | An Arme, *Backeyen* | |
| Guts – *Perot* | The priuy part, *Perot* | (Malay *perut* 'belly') |
| a Cyuet Cat – *Gatto d'algalia* | A Muske-cat, *Gatto Dalgalia* | an *Italian* phrase passed on as Malay |

Herbert's Javanese section ("The people in Iaua call these thus") reproduces van Neck's "Some Iauanish words"
(*Alomba*, *Vrangy*, *Cartaes*, *Serpy*), and his "numbers in the Malayan Speech" reproduce van Neck's
"Counting in the Molucas tongue".

## Wider transmission (stemma sketch)

```
Dutch original of van Neck's journal (1600) ──► English translation (London, 1601) ──► Herbert 1634 ──► Herbert 1638 (further drift: Tambagle "Copper" → "Lead")
          │
          └─► Dutch compilers ──► Mandelslo in Olearius (Eng. 1669)      [shares forms, not Herbert's errors]
                              └─► Dapper/Montanus ──► Ogilby, Asia (1673) [shares forms, not Herbert's errors]
```

A translation error in the 1601 English edition is visible by comparison with the Dutch branch: van Neck (Eng.)
"Newes – *Yrotdon*" vs Mandelslo "*Yrotdon* the nose" — the English translator apparently read Dutch *neus*
("nose") as "news".

## Why it matters

1. Herbert's list is not independent evidence for Malay as heard by an Englishman in the 1620s; it is a
   corrupted copy of a list collected by the second Dutch voyage in 1598-99, with roughly 30% of glosses wrong.
2. It is a clean, quantifiable example of how early modern travel writers manufactured linguistic
   authority, and of how a vocabulary's errors can be used stemmatically to reconstruct its circulation.
3. It demonstrates the method: the lineage detector found this without being told to look.
