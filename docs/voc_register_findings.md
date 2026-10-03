# VOC "lost vocabularies" register: findings (2026-10-03)

Source: GLOBALISE VOC transcriptions v2 (CC0), 4.79M pages, full-text index in
`Historical Mysteries/globalise-drugs/data/voc.sqlite` (read-only). Pipeline: `src/voc_register.py`
(987 hits) -> agent classification (`data/work/voc_register/classified_*.jsonl`, 633 relevant) ->
`src/voc_register_merge.py` -> `data/work/voc_register/register.csv` (65 works). Fate check of 14
works in `data/work/voc_register/fates.json` (light pass; "unknown" = nothing found quickly).

## Main result: Van Gollenesse's Malabar glossary (1743) survives in The Hague

- Stein van Gollenesse's 1743 Cochin memoir for Siersma ends with "notes in the form of a dictionary
  of the chief kingdoms, lands, towns, bazaars, pagodas, rivers, festivals and names in Malabar
  arranged in alphabetical order".
- The 1908 Madras edition (Dutch Records No. 1, Dutch text from the Madras copy) does not contain it;
  Galletti's translation (*The Dutch in Malabar*, 1911) marks it "[missing]".
- The Hague copy, NL-HaNA 1.04.02 inv. 2601, fol. 161-191 = scans 0371-~0440, contains it
  (volume index at scan 0008: "Een Mallabars woordenboek behorende tot voorsz. Memorie").
  About 150-200 alphabetical entries (Malayalam terms, castes, titles, places, calendar), explained
  in Dutch. HTR text: `data/work/voc_register/gollenesse/2601_0370-0442.txt`. A second copy may be
  in inv. 4451 (enclosure list at scan 0163) - not yet checked.
- Literature search found no edition of the glossary. Needs a specialist check (Kerala/VOC scholars).

## Confirmed or likely lost (VOC mentions, no surviving copy found)
- Wreede's Dutch-Khoekhoe vocabulary, Cape 1663 (3998_0527; enclosures 3997_1686, 3998_0010).
  Literature: lost. No copy in inv. 3996-4000 (the one garbled candidate page, 3998_1549, is an
  upside-down muster roll).
- 300-word Pangsoya (Siraya) vocabulary, Formosa ~1636 (1121_0635). Undiscussed.
- Heurnius's Uliasser vocabulary, Ambon 1634 (1113_1945). Undiscussed.
- Sangirese-Spanish dictionary saved from Fr Manuel Español's burned books, Ternate 1678. Undiscussed.
- Dutch-Malagasy vocabulary sent from the Cape 1663 with Balan's report (3997_1979). Undiscussed.
- Elbracht's Dutch Persian grammar, Bengal 1778. Undiscussed.

## Copies transcribed in the archive (besides the glossary)
- Ruell's Sinhala grammar (1699 MS): inv. 1616, scans 0386-0387, 0451 (printed Amsterdam 1708).
- Malay orthography/prosody treatise, Batavia ~1718: inv. 1902, scans 0757, 0766.
