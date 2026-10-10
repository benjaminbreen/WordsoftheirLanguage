# Reverse-bibliography pass

Goal: list every word list / vocabulary / dictionary / grammar of a non-European language (or creole,
pidgin, jargon) that an early bibliography records, then find the ones that today's linguistic literature
does not cite: forgotten items, especially MANUSCRIPTS and obscure printed places (periodicals, appendices
to travel accounts, small pamphlets).

## Steps
1. Get the bibliography's OCR text from the Internet Archive (find the item via advancedsearch.php; download
   <id>_djvu.txt). Work through your assigned sections systematically.
2. Parse entries into rows: language as named, compiler/author, short title or description, year, kind
   (printed / manuscript), where printed or where the manuscript was (owner/library as stated), page ref in
   the bibliography.
3. Map the language to a Glottolog code: `python src/glotto_refs.py "<name>"` (or import find/refs from
   src/glotto_refs.py). Then check whether the item is among Glottolog's references for that language
   (match on author surname + year ± 2, or title words). Glottolog's bibliography is the best single proxy
   for "known to linguists".
4. For items NOT in Glottolog's references: run a quick web check (author + language + "vocabulary"),
   and for manuscripts try to find the present location (library catalogue / web).
5. Prioritise: thinly documented or extinct languages (see data/work/gaps.csv), manuscripts, early dates,
   larger lists.

## Output
- data/work/biblio/<source>_all.csv: every parsed entry (language, glottocode, author, title, year, kind,
  location_as_stated, bib_page, in_glottolog yes/no/unclear)
- data/work/biblio/<source>_orphans.jsonl: items not in Glottolog, after web check, one JSON per line:
  {source, bib_page, language_as_named, glottocode, author, title, year, kind, location_as_stated,
   present_location (if found), url (only if actually opened), web_check, status: forgotten|known_elsewhere|lost|unclear,
   priority 1-5, notes}
- data/work/biblio/<source>_log.md: method, counts, problems.
Be honest; do not invent locations or URLs.
