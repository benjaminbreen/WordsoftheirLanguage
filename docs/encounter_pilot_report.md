# Pilot: elicitation and contact artifacts in 18 early modern wordlists

Date: 2026-10-01. Data: 18 lists, 3,110 entries (EEBO-TCP extractions).

## 1. Computational detectors (string distance over sound classes)

Evaluated against protocol annotations (confidence ≥ 0.6):

| detector | precision | recall |
|---|---|---|
| loan (donor-language match) | 0.21 | 0.07 |
| ostension (rare-colexification neighbour match) | 0.05 | 0.17 |
| interactional (match to target's WHAT/THIS/NOT...) | 0.00 | 0.00 |
| phrase gloss (regex) | 0.88 | 0.39 |

Conclusion: lexical-distance detectors are not a viable primary method. They may serve as a
cheap recall booster or for corpus-scale prioritisation, not for counting.

## 2. Protocol annotation (LLM annotators, evidence required)

First pass, all 3,110 entries: ok 2,173 · phrase 486 · loan 134 · inflected 57 · ostension 35 ·
print/translation error 30 · wrong language 9 · interactional 8 · uncertain 88.

## 3. Reliability (independent second pass with lookups, 867 entries, 7 lists)

| | agreement | Cohen's κ |
|---|---|---|
| fine categories | 0.91 | 0.68 |
| artifact vs not | 0.92 | 0.63 |

Per list κ: Boothby 0.89, Trinidad 0.81, Pegu 0.71, Saami 0.69, Greenland 0.66, Chile 0.55, Rosier 0.24
(Rosier has very few positives, so κ is unstable). 63 artifacts were assigned the same category by both.

Main disagreement sources (80 rows): ok↔loan (22; mostly whether old, established loans count),
ok↔uncertain (20), ok↔phrase (descriptive vs. speech-act glosses), inflected↔ostension (a possessed form
that also names the wrong body part). All are protocol-definition issues, fixable by tightening rules:
- loans: separate `loan_recent` (European / contact-period donor) from `loan_established` (pre-contact);
- phrase: only sentences, questions, requests, imperatives;
- allow two labels (e.g. inflected + ostension: Lokono *da-siri* "my nose" given for "lips");
- obligatorily possessed nouns (Algonquian m-/n-, Arawakan) are `ok` unless the possessor is unexpected.

## 4. Validation against specialist literature

Agreed artifacts that the literature already records: Herckmans's Quechua loans (Sánchez 2020, using the
Schuller edition entry by entry); Lokono da- 'my' (Warner 1899). This is evidence the annotations track
expert judgement — and a reminder that per-list findings are often known; the contribution is the rates.

## 5. Candidate anecdotes (both annotators agree, or one annotator with web verification)

- Wood 1634: "I" = *Kean*, "you" = *Nean* — pronouns swapped (Massachusett *neen* I, *ken* you), confirmed
  by Wood's own sentences (*Chesco kean* "you lye").
- Dudley 1595 (Lokono): heaven = *wiwa* 'star'; water = *bara* 'sea'; lips = *da-siri* 'my nose';
  gums = 'my teeth'; forehead = 'my head'; toes = 'my nail'; wheat = *marishi* 'maize'.
- Olearius (Kalaallisut, 1650s): father = *ui* 'husband', mother = *nuliaq* 'wife' (pointing at a couple);
  flesh = *tuttu* 'reindeer'; woman = *Kona* (Norse/Danish), taken from Greenlanders in Denmark.
- Burrough 1557 (Kildin Saami): "2" = *Noumpte* < 'the other, second'; Russian *sapogi* 'boots'.
- Rosier 1605: pease = *skamon* 'maize' (new crop named with the old staple).
- van Neck 1601 (Dutch → English): *Bapa* 'father' glossed "farther off" (*vader/verder*); *obat bedil*
  'gunpowder' glossed "spicerie" (*kruit/kruiden*); *Yrotdon* 'nose' glossed "newes" (*neus*).
- Ogilby 1671 (Tupi): *Coaraci* 'sun' printed as "a Son"; *Caraibebe* 'angel' printed as "an Angle".
- Rochefort 1666 (Island Carib): Spanish goods words (*aguja, alfiler, arca, puerco, peine*);
  *Pikenine* < Portuguese *pequenino*; Cariban men's-register words concentrate in M. entries (odds ≈ 5.6).

## 6. Typology emerging from the pilot: where in the chain errors enter

1. elicitation (ostension, interactional, pronoun reversal, time-word confusion);
2. informant's grammar (captured possessors: *da-*, *n-*, -*ga*, -*ko*);
3. intermediary languages (Cariban men's register, Quechua in Mapudungun, Malay in Mon list, Norse/Danish in Greenlandic);
4. translation between European languages (Dutch → English homophones);
5. print shop (Son/Sun, Angle/Angel, column swaps);
6. later copying (Herbert's re-glossing).

## 7. Next steps

1. Tighten protocol (section 3), re-run both passes on the 867 paired entries, target κ ≥ 0.75.
2. Human spot-check of `out/spotcheck_sample.csv` (50 entries) for a precision estimate.
3. Scale corpus to hundreds of lists (18th–19th c.: Internet Archive / HathiTrust / BHL / Trove), dedupe by lineage.
4. Code list-level covariates (collector type, contact duration, interpreter mentioned, region, date) and model rates.
