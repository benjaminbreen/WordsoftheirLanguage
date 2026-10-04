# TCP (Evans + ECCO) wide-net log

## Corpora
- Bulk source: Hugging Face `Vintage-LLM/EVANS` (5,012 texts, 4 parquet, ~230 MB) and `Vintage-LLM/ECCO` (3,101 text parts ≈ ECCO-TCP ~2,400 works, 3 parquet, ~250 MB); CC0, converted from TCP XML (OTA handles 20.500.14106/<id>). Stored in data/raw/evans, data/raw/ecco (gitignored). GitHub per-text repos not needed.
- Note: TCP keyed essentially only English-language texts (language field: 8,110 eng, 3 other), so bilingual Native-language imprints (Eliot, Zeisberger, Mather's Iroquois) are mostly absent or partial.

## Detector (src/detect_tcp.py)
- Pass 1 (`python src/detect_tcp.py`, PYTHONPATH=src): reuses detect.scan_text; rarity over EEBO+Evans+ECCO combined (docs<=8, count<=60): 423,347 rare tokens; 5,908 spans in 1,280 texts -> tcp_candidates.parquet, tcp_texts.parquet. Top ranks dominated by false positives (Ossian, Chatterton/Rowley, Linnaean Latin, Welsh/Gaelic charters, place-name gazetteers).
- Pass 2 (`--lines`): pair-lines detector for alternating-line / table vocabularies: 766 spans in 236 texts (tcp_listspans.parquet); 118 texts with >=5 distinct glosses reviewed.
- Pass 3 (scratch): italic-foreign + gloss density (21 texts, tcp_italic.parquet) and keyword regex ("vocabulary of the", "in the Indian language", numerals, Lord's prayer) over both corpora (57 texts).

## Triage (~180 texts looked at; top 100 of pass 1, all 118 of pass 2, all of pass 3)
Real lists: Carver (Ojibwe, Dakota), Hawkesworth/Parkinson (Guugu Yimithirr, Tahitian, Māori, Savu, numerals), Cook 3rd voyage US ed. (Tasmanian), Pope 1792 (Creek), Burges 1790 (Anglo-Indian glossary), Trusler 1788 (Khanty/Mansi/Mordvin; Aleut/Yupik/Greenlandic; Saami), Drury (Malagasy), Stedman (Sranan), Psalmanazar (fake). Also English cant list in Thomas Mount's Confession (N35358, 1791; out of scope), Coxe Romansh vocab (European), Norn Lord's Prayer (European).
Treaty records (Lancaster 1744, Easton 1758) only names/titles. Captivity narratives (How 1748, Smith 1799, Gilbert 1784, Bunn 1796) mention Indian speech but contain no lists.

## Novelty checks
- Pope Creek: web search found only historical/bibliographic mentions; Pilling not verified -> "obscure".
- Burges glossary: scroll.in article + catalogue (glossary pp.144-147 in 1817 ed.); no lexicographic use found -> "obscure".
- Others are standard known sources.
