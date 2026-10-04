# Wide-net search for new/undescribed early modern glossaries and word charts

Goal: find word lists, vocabularies, glossaries, phrase lists, numeral charts or comparative word tables
of non-European languages (or creoles/pidgins/trade jargons) made c. 1500–1850, printed or manuscript,
that are NOT already known to linguists — or are known only as a citation but never edited/used.

## Output (one JSON object per line) to data/work/widenet/<source>.jsonl
{ "source": "<your source key>", "title": "...", "url": "<stable link to item/page>",
  "date": "...", "kind": "printed|manuscript", "holder": "...", "shelfmark_or_id": "...",
  "language_as_named": "...", "modern_id": "... (Glottolog name/code if possible)",
  "size": "approx. entries/pages", "evidence": "short quote or description proving it is a word list (≤ 30 words)",
  "novelty": "new | obscure | known", "novelty_basis": "what you searched (Glottolog refs, Google Scholar, WorldCat, standard bibliographies) and found",
  "language_status": "thinly documented / extinct / well documented", "priority": 1-5, "notes": "..." }

## Rules
- Precision over volume: every row must be verified to actually be a word list (open it / read the page / read the catalogue entry).
- Novelty check every candidate before marking new/obscure: search the language name + compiler/title in Google Scholar / web, check Glottolog references for that language where possible, and standard bibliographies (Pilling for North America; Viñaza for Spanish colonial; Streit; Cust; Doke for Africa). "known" if it is cited as a source in linguistic literature.
- Value: highest priority = extinct or thinly documented languages, early dates, larger lists, manuscripts never edited.
- Be honest; say "unclear" when unclear. No fabricated URLs: only include links you actually opened.
- Keep a short log of queries at data/work/widenet/<source>_log.md.
- Gap list of thinly documented languages: data/work/gaps.csv (Glottolog: extinct/nearly extinct, wordlist-or-less).
- Already in the project (skip): the 19 site tables (README.md), JCB pilot triage (data/work/jcb/triage_*.csv), VOC register (data/work/voc_register/register.csv).
