# Triage of JSTOR Early Journal Content candidates (batch b<N>)

Input: data/work/jstor2/batches/b<N>.jsonl — one article per line: identifier (Internet Archive item id,
https://archive.org/details/<identifier>), title, year, creator, how (why it was harvested), snippets.

For EVERY line decide:
1. Title screen. If the title is plainly not about a non-European language word list (e.g. English dialect,
   classical philology, ornithology without native names), mark relevant=false with a 2-5 word reason.
2. Otherwise open the text: https://archive.org/metadata/<id> gives the file list; download the *_djvu.txt
   (or .txt). Find whether the article PRINTS a word list / vocabulary / numerals / phrase list of a
   non-European language, creole, pidgin or jargon (not just discusses one). Count entries roughly.
3. For real lists: identify the language (modern name) and its Glottolog code with
   `.venv/bin/python src/glotto_refs.py "<name>"` (prints Glottolog references, pre-1900 ones listed).
   in_glottolog = yes if this article (author + year ±1, or title) is among the references; else no.
4. Find the page(s) of the list: leaf numbers in the IA item (the djvu.txt is in page order; use
   *_djvu.xml OBJECT/PARAM PAGE names or count pages; leaf n = archive.org/details/<id>/page/n<leaf>).

Write data/work/jstor2/triage_b<N>.jsonl — one JSON per input line:
{identifier, title, year, relevant: true|false, reason (if false), is_list: true|false,
 language_as_named, modern_language, glottocode, in_glottolog: yes|no|unclear, entries_est,
 leaves: [..], collector, place, heard (date of collection if stated),
 priority: 1-5 (5 = not in Glottolog AND thinly documented/extinct language or early date; 1 = known/marginal),
 note}
Rules: precision matters; read the text before claiming a list exists; do not invent leaves.
Use .venv/bin/python. Be polite to archive.org (≤2 requests/second).
Return: counts (screened, opened, real lists, not in Glottolog) and the top 10 by priority, one line each.
