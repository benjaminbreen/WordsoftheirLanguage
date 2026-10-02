# Annotation protocol: elicitation and contact artifacts in historical wordlists

You annotate every entry of one or more extracted wordlists (`*.entries.csv`: gloss_as_printed,
form_as_printed, section_heading, note). The language each list records is given to you. Your job is to
decide, entry by entry, whether the printed pairing shows an **artifact of the encounter** in which it was
collected, and to back every positive call with concrete evidence.

Write one JSON object per entry (every row, including unremarkable ones) to the output file:

```json
{"list": "trinidad", "n": 12, "gloss": "...", "form": "...",
 "category": "ok | loan | ostension | interactional | inflected | phrase | wrong_language | print_error | uncertain",
 "subtype": "free text, e.g. donor language, or 'kin term for pointed person', or 'question word'",
 "evidence": "modern form(s) and gloss you compare against, with language name, e.g. 'Lokono wiwa \"star\"'",
 "confidence": 0.0,
 "comment": "one sentence"}
```

Categories (choose the single best; use `ok` when nothing is remarkable):

- **loan**: the form is a word from another language (European: Spanish, Portuguese, French, Basque, Dutch,
  English, Danish/Norse...; or a lingua franca / neighbouring language: Malay, Arabic, Persian, Quechua,
  Cariban, Tupi, trade jargon). Give the donor word in `evidence`.
- **ostension**: the form is a real word of the language but means something *related* to the gloss,
  as happens when a collector points: e.g. "star" given for "heaven", "nail" for "finger", "brother" for
  "boy", "my hand" for "hand" is NOT this (that is `inflected`). Give the actual meaning in `evidence`.
- **interactional**: the form is a question, answer, deictic, negation, greeting or comment ("what is it?",
  "I don't know", "this", "no", "give me") recorded as if it were the word for a thing.
- **inflected**: the form carries possessive, plural, or person marking that the gloss does not show
  (e.g. Arawakan da- "my", Algonquian n-/k- "my/your" on body parts or kin). Mark this only if you can name the affix.
- **phrase**: the gloss itself is a phrase or sentence, correctly rendered (not an artifact; we count these).
- **wrong_language**: the form belongs to a different language than the list's (e.g. a Malay word in a
  Mon list) but is not a loan established in the target language.
- **print_error**: misprint, column misalignment, gloss attached to the wrong form (e.g. alphabetical
  list sorted by gloss with forms shifted).
- **uncertain**: something looks odd but you cannot support a category with evidence.

Rules:

- No evidence, no flag. If you cannot cite a modern or historical comparison form, use `ok` or `uncertain`.
- Prefer `ok` when a gloss/form pair is simply a different but ordinary translation choice.
- Known colexifications are `ok` (e.g. man/person, wife/woman, hill/mountain, flesh/meat, tree/wood,
  arm/hand in languages that colexify them).
- Spelling differences from modern orthography are expected; do not flag them.
- `confidence` is your probability that the category is right.
- Do not consult or reproduce more than brief quotations of copyrighted works; dictionaries may be used for
  short form lookups. You may use web search sparingly for specific word checks.
- Work in your own scratch folder for helper scripts; other annotators run in parallel.
