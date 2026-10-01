# Triage protocol: candidate vocabulary spans (EEBO-TCP)

Each input line in `data/work/triage2/batch_NN.jsonl` is a candidate span: metadata and a
~2,200-character `snippet` of the transcription (Markdown; italics `*x*` are as printed,
`[^n]` are footnote markers, `•` / `〈◊〉` are illegible characters).

For EVERY input line write exactly one JSON line to `data/work/triage2/out_NN.jsonl`:

```json
{"span_id": "...", "tcp_id": "...",
 "is_vocab": "yes | partial | no",
 "mode": "list | table | inline | dialogue | glossary_index | none",
 "european_only": true,
 "label_as_printed": "exact heading or ethnonym words used by the source, verbatim, or null",
 "place_as_printed": "place named near the vocabulary, verbatim, or null",
 "region": "broad world region the source itself is describing (e.g. 'New England', 'Madagascar', 'Guinea coast'), or null",
 "n_forms_visible": 0,
 "sample_pairs": [["gloss as printed", "form as printed"]],
 "interest": 0,
 "why": "one short sentence"}
```

Definitions:

- `is_vocab = yes`: the snippet contains words of a non-European language (Americas, Africa,
  Asia, Pacific, Arctic, also Sami, Romani, Basque, Turkic, Arabic etc.) paired with or explained
  by European glosses: a list, a table, a dialogue, or a run of "which they call X" glosses.
  `partial`: only a few (2-4) such words, or the vocabulary is at the snippet edge.
  `no`: anything else, including place-name lists, personal names, Latin/Greek/Hebrew
  philology, European-language dictionaries, herbals with Latin plant names, cant, divination
  terms, gibberish in plays. (Do note a play or satire that invents a "foreign" language:
  mark `is_vocab = partial`, `why` starting "PSEUDO:".)
- `european_only = true` when every foreign form is from a European classical/modern language
  (Latin, Greek, Hebrew, French, Spanish, Dutch, Welsh, Irish ...).
- `sample_pairs`: up to 5 pairs copied EXACTLY as printed, including spelling and accents.
- `interest`: 0 = not a vocabulary; 1 = well-known/major language or famous source (Hakluyt,
  Purchas, Roger Williams, Arabic, Turkish, Malay, Nahuatl ...); 2 = a vocabulary of a less
  documented people or a surprising location in the book; 3 = something odd that a historian
  or linguist should look at: unlabeled language, mixed or contact forms, a vocabulary in an
  unexpected genre, suspected fabrication, an obscure people.

Rules:

- Do NOT identify the language by modern name in `label_as_printed` / `place_as_printed`;
  copy the source's own words. You may give your guess only inside `why`, prefixed "guess:".
- Never correct, modernise or normalise spellings.
- Do not skip lines. Output must be valid JSONL (one object per line, no prose).

## v2 additions

Snippets are now centred on the densest vocabulary evidence (~2,800 characters). Add two fields:

- `continues`: true if the vocabulary visibly continues beyond either edge of the snippet.
- `contact_flags`: list of forms (as printed) that look like European loans, pidgin/trade forms, or
  words the collector seems to have mis-elicited (e.g. a word meaning "what?" or "finger" given
  as a name). Empty list if none.

Work in your own scratch subfolder if you write helper scripts (e.g. `.../scratchpad/t2_NN/`);
other agents run in parallel.
