# Wordes of their Language

A catalogue of vocabularies of non-European languages printed in early modern books, shown as
they appear on the page beside a careful transcription.

European travellers, missionaries and merchants often printed short word lists of the languages
they encountered: a table at the end of a chapter, a glossary in a voyage account, a page of
numerals. Some of these are among the earliest records of their languages, and some record
languages that are no longer spoken. They are scattered across thousands of books and easy to
miss. This project finds them, puts each one next to an image of the original page, and makes
the words searchable and comparable.

The title comes from Stephen Burrough's 1557 account of the Kola coast, printed by Hakluyt:
*"I obserued certaine wordes of their language."*

## What is here now

23 tables in 22 languages (3,559 entries), 1580–1834.

| Language | Source | Printed |
|---|---|---|
| Laurentian (St Lawrence Iroquoian) | Jacques Cartier, *A Shorte and Briefe Narration* | 1580 |
| Kildin Sami | Stephen Burrough, in Hakluyt, *Principal Navigations* | 1599 |
| Lokono (Arawak) | Robert Dudley's voyage, in Hakluyt | 1600 |
| Malay | Jacob van Neck, *The Iournall, or Dayly Register* | 1601 |
| Mon | *A True and Large Discourse* (first East India Company voyage) | 1603 |
| Powhatan | John Smith, *A Map of Virginia* | 1612 |
| Eastern Abenaki | James Rosier, in *Purchas his Pilgrimes* | 1625 |
| Massachusett | William Wood, *New Englands Prospect* | 1634 |
| Malay (copied from van Neck) | Thomas Herbert, *A Relation of Some Yeares Travaile* | 1634 |
| Narragansett | Roger Williams, *A Key into the Language of America* (ch. I–II) | 1643 |
| Malagasy | Richard Boothby, *A Briefe Discovery … of Madagascar* | 1647 |
| Island Carib | César de Rochefort, *The History of the Caribby-Islands* | 1666 |
| Kalaallisut (Greenlandic) | Adam Olearius, *Voyages and Travells of the Ambassadors* | 1669 |
| Mapudungun | Elias Herckmans, in John Ogilby, *America* | 1671 |
| Tupinambá | John Ogilby, *America* | 1671 |
| Sami | Johannes Scheffer, *The History of Lapland* | 1674 |
| Sinhala | Robert Knox, *An Historical Relation of the Island Ceylon* | 1681 |
| Ge'ez, Amharic and Oromo | Hiob Ludolf, *A New History of Ethiopia* | 1682 |
| Pidgin Delaware | Gabriel Thomas, *An Account of Pensilvania* | 1698 |
| Malayalam (Malabar terms) | J. V. Stein van Gollenesse, *Mallabars woordenboek* (manuscript, Nationaal Archief, VOC 2601) | 1743 |
| Uab Meto (Timorese) | W. van Hogendorp, in *Verhandelingen van het Bataviaasch Genootschap*, deel 2 | 1780 |
| Muskogee (Creek) | John Pope, *A Tour through the Southern and Western Territories* | 1792 |
| Meriam Mir | "Some Account of the Natives of Murray's Island", *United Service Journal* | 1834 |

Each table has a page with the scanned pages, the transcription, and a panel for the selected
entry. Clicking a line on the scan finds its entry, and the reverse. Entries have permanent links
for citation, and every table can be downloaded as CSV or JSON.

## How it works

1. **Finding tables.** A detector runs over the ~60,000 transcribed books of
   [EEBO-TCP](https://textcreationpartnership.org/) and flags passages where words that are rare
   everywhere else in the corpus sit beside everyday English glosses (*water*, *head*, *knife*).
   Candidates are reviewed and transcribed with original spelling kept.
2. **Finding the pages.** Each book is matched to a public-domain scan on the Internet Archive,
   usually the John Carter Brown Library's copy. The table's pages are located from the scan's
   OCR, and each entry is aligned to its printed line. Positions that are estimated rather than
   matched are marked as such.
3. **Identifying the language.** Separately from the source's own label, the printed forms are
   compared against ~17,000 modern wordlists ([ASJP](https://asjp.clld.org/),
   [Lexibank](https://lexibank.clld.org/)). A match is reported only if it beats what shuffled
   lists achieve; otherwise the site says it cannot tell. Reference lists that descend from the
   same historical source are removed before comparison.
4. **Notes.** Some entries carry short notes (a loanword, a word meaning something nearby, a
   printing or translation slip). These are drafts written to a fixed protocol and have not yet
   been reviewed by specialists.

## Repository layout

```
site/        Astro website (static; deploys to Vercel with Root Directory = site)
src/         Python pipeline: detection, scan matching and alignment, identification, site data
docs/        Protocols and working notes
data/        Extracted transcriptions, annotations, source mappings (raw corpora not included)
```

## Running the site locally

```bash
cd site
npm install
npm run dev
```

The pipeline needs Python 3.12 and the source corpora (EEBO-TCP, ASJP, Lexibank, Glottolog),
which are downloaded separately and not committed. See `site/README.md` for how tables are added.

## Plans

- More tables from English print before 1700, and the rest of Roger Williams's *Key*.
- Eighteenth- and nineteenth-century sources (Internet Archive, HathiTrust, the Biodiversity
  Heritage Library), where far more vocabularies were printed and fewer have been studied.
- French, Dutch, Spanish and Portuguese sources, with glosses in those languages.
- Colonial newspapers and digitised manuscripts, which are the most likely places to find
  vocabularies of languages that are otherwise poorly documented or unknown.
- Review of the draft notes by specialists, and a way for readers to submit corrections.

## Data and licences

- Transcriptions derive from EEBO-TCP, released into the public domain (CC0).
- Page images are public-domain scans from the Internet Archive; each table names the holding
  library.
- Comparison data come from ASJP and Lexibank (CC BY 4.0); classification from
  [Glottolog](https://glottolog.org/).

Many of these words belong to living communities and to their ancestors. Identifications are
provisional, and corrections and context from people who know these languages are welcome.

## Credit

Made by [Benjamin Breen](https://benjaminpbreen.com) ([Res Obscura](https://resobscura.substack.com)).
