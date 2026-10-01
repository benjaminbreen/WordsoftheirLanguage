# Wordes of Their Language

A census of non-European vocabularies embedded in English printed books (EEBO-TCP, 1473–1700), with
blind language identification against ASJP + Lexibank and detection of copying between books.

Live (private) site: https://claude.ai/artifact/S9ciubhA6ECD4CKZBd7V2E

## Pipeline

| Step | Script | Output |
|---|---|---|
| Corpus token frequencies | `src/build_freq.py` | `data/work/token_freq.parquet` |
| Detector (rare-form × gloss adjacency, naming cues) | `src/detect.py` | `data/work/candidates.parquet` |
| Peak windows | `src/build_windows.py` | `data/work/windows.parquet` |
| LLM triage (protocol in `docs/triage_protocol_v2.md`) | agents | `data/work/triage2/out_*.jsonl` |
| Diplomatic extraction | agents | `data/work/extract*/*.entries.csv` |
| Identification | `src/identify2.py` | per-list JSON |
| Leave-lineage-out benchmark + null calibration | `src/benchmark.py` | `out/benchmark.json` |
| Transmission network | `src/lineage2.py` | `data/work/lineage_vocab_edges.parquet` |
| Website | `src/build_site_data.py`, `src/build_site.py` | `out/site/index.html` |

Raw data (not in git): `data/raw/eebo` (HF `Vintage-LLM/EEBO`), `data/raw/asjp_repo` (lexibank/asjp),
`data/raw/lexibank_repo` (lexibank/lexibank-analysed), `data/raw/glottolog_cldf`, `data/raw/leme`.

## Results so far

- Detector recall: 31/35 LEME travel lexicons within the top 1,000 texts.
- Census v0: 115 books with non-European vocabulary (77 not matched to LEME's bibliography).
- Benchmark (threshold z ≥ 4.8, above the max of 100 null runs): 7 correct, 3 abstentions, 0 wrong.
- Blind identifications agree with Genetz 1895 (Burrough = Kildin Saami), Warner 1899 (Dudley's Trinidad =
  Arawak, da- 'my'), Blagden in Foster 1940 (Pegu = Mon). See `docs/novelty_check.md`.
- New: Herbert's 1634 "Malayan Tongue" is a re-sorted copy of the 1601 English van Neck list
  (`docs/case_herbert_vanneck.md`).
