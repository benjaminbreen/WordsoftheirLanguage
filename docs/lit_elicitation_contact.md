# Literature review: mis-elicitation and contact artifacts in historical wordlists

Prepared 2026-10-01 for the planned paper (corpus-scale rates of interactional forms, ostension errors, body/possessive elicitation, contact loans, and whole-list intermediary languages in printed wordlists c.1500-1900).

Legend: **[C]** = confirmed via a web source fetched/searched in this session (URL given). **[I]** = my inference or recollection, not verified this session; check before citing. Bibliographic details marked [I] should be verified in a library catalogue.

---

## A. Has anyone done an aggregate / quantitative study?

**Short answer: not that I could find.** The literature is rich in (i) single-source philology (one list, one voyage, one language), (ii) contact-language reconstructions that *use* wordlists as evidence for a pidgin, and (iii) single-loanword diffusion studies. I found no study that codes many historical wordlists across regions for a taxonomy of elicitation/contact artifacts and reports rates by collector type, date or region. Computational work on large wordlist collections (Lexibank, ASJP, CHIRILA) treats historical-source noise as a data-quality nuisance to filter, not as an object of study.

### A1. Single-source philology that identifies the artifact types (closest precedents)

- **Haviland 1974**, "A last look at Cook's Guugu-Yimidhirr word list", *Oceania* 44(3): 216-232. [C: bibliographic data at https://pages.ucsd.edu/~jhaviland/JBHPublications.html and search result] Re-elicits Cook/Banks's 1770 list item by item with speakers; the canonical model of "re-checking an early list against a modern language". It is the source behind the debunking of the kangaroo legend (see B).
- **Koch 2016**, "Documentary sources on the Ngarigu language: the value of a single recording", in Austin, Koch & Simpson (eds.), *Language, Land & Song: Studies in honour of Luise Hercus*, London: EL Publishing, 145-157. [C: https://www.elpublishing.org/docs/6/01/Chapter-11-Koch.pdf, text extracted] Directly relevant to categories (4)/(5): Koch states that Lhotsky's 1834 Monaro wordlist "contains a number of terms from Sydney Pidgin English (e.g. <waddi> 'tree', <gibba> 'stone', <narang> 'little')" — "by my estimation at least eight items, with five more possible" — and may include words from a neighbouring language picked up en route. This is exactly the kind of per-list count the paper would generalise; Koch does it by hand for one list.
- **Simpson 2016**, "Working verbs: the spread of a loan word in Australian languages", same volume, 244-262. [C: https://www.elpublishing.org/docs/6/01/Chapter-17-Simpson.pdf] Maps one loan ('work') across many Australian sources incl. historical vocabularies; a geographical, not rate-based, design. Notes uncertainty whether *yakka* 'work' in Biri/Yagara/Yugarabul vocabularies is original or a loan — i.e., the contact-layer ambiguity the paper must model.
- **Troy 1994**, *Melaleuka: a history and description of New South Wales pidgin*, PhD, ANU. [C: https://openresearch-repository.anu.edu.au/handle/1885/112648] Reconstructs NSW Pidgin from colonial sources (NSW and Victoria, late 18th to mid 19th c.); key reference for identifying pidgin items (*budgeree*, *bail/baal* 'no', *gibber*, *waddy*) inside lists labelled as local languages. Note *baal* 'no' is a negator that circulates as vocabulary — directly relevant to category (1).
- **AustKin workshop "Garbled voices from the archives: Restoring Aboriginal words and meanings in historical sources"**, ANU, 15-16 April 2014. [C: https://slll.cass.anu.edu.au/events/garbled-voices-archives-restoring-aboriginal-words-and-meanings-historical-sources ; https://paradisec.org.au/blog/?p=7956] Shows a self-aware community of practice (Koch, Nash, Simpson, Troy and others) working on interpretation of early Australian sources; I found no resulting aggregate publication.
- **CHIRILA** (Bowern): database of contemporary and historical Australian lexical sources with a three-point transcription-reliability rating per source. [C: https://campuspress.yale.edu/clairebowern/category/research/chirila-research/ ; https://www.researchgate.net/publication/370685100_Managing_Historical_Data_in_the_Chirila_Database] Bowern's quantitative work (e.g. phonotactics papers) restricts to linguist-compiled sources because historical sources "vary extensively" [C: https://arxiv.org/pdf/2002.00527]. CHIRILA is the closest thing to a corpus of historical lists *with* reliability metadata — a potential validation set and a must-cite.
- **Wikibook "A reference guide to the spelling of Australian Aboriginal languages in early sources"**. [C: https://en.wikibooks.org/wiki/A_reference_guide_to_the_spelling_of_Australian_Aboriginal_languages_in_early_sources] Orthographic, not elicitation-focused.

### A2. Contact languages reconstructed from wordlists (category 5 precedents)

- **Drechsel 2014**, *Language Contact in the Early Colonial Pacific: Maritime Polynesian Pidgin before Pidgin English*, Cambridge UP. [C: https://www.cambridge.org/core/books/language-contact-in-the-early-colonial-pacific/9E4DA477392ABDA61F4C0CA7D3812FFF] Central thesis: many early European wordlists of "Tahitian/Hawaiian/Māori" record a Polynesian-based pidgin rather than the vernacular. This is the strongest prior claim for category (5); it is qualitative and contested (reviews should be checked). Must engage.
- **Bakker 1989**, "'The language of the coast tribes is half Basque': A Basque-American Indian pidgin in use between Europeans and Native Americans in North America, ca. 1540-ca. 1640", *Anthropological Linguistics* 31(3-4): 117-147. [C: https://glottolog.org/resource/reference/id/131183] Plus Bakker's papers on Basque loans in Mi'kmaq (e.g. *atlai* 'shirt' < *atorra*, *elege* 'king' < *errege*) and the 17th-c. Basque-Icelandic glossaries. [C: https://en.wikipedia.org/wiki/Mi%27kmaq_language ; Basque-Icelandic: https://buber.net/Basque/?p=837 ; ASJU papers at https://ojs.ehu.eus/index.php/ASJU/article/view/8227 — exact titles I]
- **Goddard 1995**, "The Delaware Jargon", in *New Sweden in America*; **Goddard 1997**, "Pidgin Delaware", in Thomason (ed.), *Contact Languages: A Wider Perspective*, Benjamins; **Goddard 2000**, "The use of pidgins and jargons on the east coast of North America", in Gray & Fiering (eds.), *The Language Encounter in the Americas, 1492-1800*, Berghahn. [C: https://glottolog.org/resource/reference/id/475881 ; https://glottolog.org/resource/reference/id/148120 ; https://www.berghahnbooks.com/title/GrayLanguage] Classic demonstration that a published "Delaware" vocabulary (Campanius; also Penn-era lists [I]) is actually a trade jargon.
- **Chinook Jargon**: 19th-c. compilers (Gibbs 1863, citing Scouler) already warned that Jargon words "crept into other vocabularies" and were "often mistaken for the Chinook itself", causing misclassification. [C: https://www.gutenberg.org/cache/epub/15672/pg15672.html] Thomason on early CJ records [C: https://public.websites.umich.edu/~thomason/papers/cj2.pdf]. Useful as an *emic* (period) awareness of category (4)/(5) contamination.
- **Pacific Pidgin English**: Clark 1979, "In search of Beach-la-mar: towards a history of Pacific Pidgin English", *Te Reo* 22: 3-64 [C: https://nzlingsoc.org/author/ross-clark/]; Baker & Mühlhäusler 1996 and Mühlhäusler, Tryon & Baker 1996 chapters in the *Atlas of Languages of Intercultural Communication* [C: https://digital.library.adelaide.edu.au/items/d8d1549c-21d9-4b1c-9b05-29eb74581de3]. Earliest-attestation glossaries of jargon items — usable as a lexicon of contact forms.
- **Pigafetta's glossaries** (Brazil 8 words, Patagonia ~90, Philippines ~160, Malay ~426): the "Malay" list is a lingua-franca list; Bausani 1960 noted copyist errors and centuries of uncritical reproduction; Thomaz on the Malay glossary. [C: https://en.wikipedia.org/wiki/Pigafetta%27s_dictionary ; https://revistes.ub.edu/index.php/Abriu/article/view/29074]
- **Hoogervorst 2024**, "Seventeenth-century Malay wordlists and their potential for etymological scholarship", *Wacana* (Oct 2024). [C: https://doaj.org/article/7bdce1cd293040128074f309cfe40d29] Critical comparison of VOC-era Malay lists — Malay as intermediary.

### A3. Loanword inventories (category 4 reference lexicons)

- **Dalgado 1913**, *Influência do vocabulário português em línguas asiáticas* (Eng. trans. *Portuguese Vocables in Asiatic Languages*, Soares 1936). Portuguese loans in 50+ Asian languages, from dictionaries (e.g. Malay 431, Tetum 774). [C: https://biblioasia.nlb.gov.sg/vol-19/issue-1/apr-jun-2023/portuguese-legacy-southeast-asia] A ready seed lexicon for Portuguese-loan detection in Asian lists.
- **Tent & Geraghty (eds.) 2003**, *Borrowing: A Pacific Perspective*, Pacific Linguistics 548; Geraghty & Tent on early Dutch loans in Polynesian. [C: https://openresearch-repository.anu.edu.au/bitstream/1885/146169/1/PL-548%20%281%29.pdf] Also Tent's "exploded myth" paper on *papālagi* — a folk etymology debunking [C: https://researchers.mq.edu.au/en/publications/exploding-sky-or-exploded-myth-the-origin-of-pap%C4%81lagi/].
- **Wallace 1857/1869** Moluccan lists already flagged Portuguese loans (*pombo, milo, testa, horas*) [C: https://lingdy.aa-ken.jp/wp-content/uploads/2012/01/120217_simon_musgrave_17_h.pdf]; Holle lists as a later colonial survey corpus [C: https://openresearch-repository.anu.edu.au/items/04727f51-6ae0-4765-8d86-aad89fc88136]. Florey's Moluccan documentation [C: https://www.eva.mpg.de/linguistics/past-research-resources/documentation-and-description/endangered-moluccan-languages-eastern-indonesia-the-dutch-diaspora/]; I did not confirm a Florey publication specifically on historical-list reliability [I].

### A4. Africa

- **P.E.H. Hair**: decades of philology of early West African vocabularies (Barbot c.1680 four languages; early 17th-c. Vai; earliest Cameroons Bantu lists of Africanus 1665/Dapper 1668 compared to modern Duala/Isuwu/Mokpe); collected in *Africa Encountered: European Contacts and Evidence 1450-1700* (Variorum). [C: https://www.routledge.com/Africa-Encountered-European-Contacts-and-Evidence-1450-1700/Hair/p/book/9780860786269 ; https://asset.library.wisc.edu/1711.dl/VFSKLPNK2NWAL8G/E/file-85482.pdf?dl] Hair is the West-African analogue of Haviland/Koch and probably the closest to a *serial* (many-lists) philologist, but still list-by-list. Must cite.
- Compagnie Royale "Dictionaire" manuscript (Senegambia) [C: https://www.academia.edu/31562976/].

### A5. Computational / large-scale wordlist work (methodological neighbours, not precedents)

- Lexibank (List et al. 2022, *Scientific Data*) [C: https://www.nature.com/articles/s41597-022-01432-0]; ASJP; automated borrowing detection (Miller & List 2023 EACL; PMC10445856) [C: https://aclanthology.org/2023.eacl-main.190.pdf ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10445856]. These detect borrowing from a *known dominant donor* in modern data; none target historical collector artifacts. Lexibank notes historical collections' sources are poorly documented and non-standardised [C: same]. Concept-list history: hiphilangsci blog [C: https://hiphilangsci.net/2018/10/31/concept-list-compilation/].
- Automated QC for modern fieldwork lists (phonotactic inconsistency, Kokborok) [C: https://arxiv.org/pdf/2510.21584] — shows the "error detection in wordlists" framing exists for contemporary data.
- Karl Franklin, "A note on eliciting words" (SIL/GIAL) — practitioner account of ostension errors (speaker names a property such as hardness instead of the object). [C: http://www.diu.edu/documents/gialens/Vol8-1/Franklin_Wordlists.pdf] Good modern-fieldwork baseline for category (2).

### A6. History of linguistics / history of knowledge frame

- Missionary linguistics series: Hovdhaugen (ed.) 1996, *...and the Word was God*; Zwartjes & Hovdhaugen (eds.) 2004, *Missionary Linguistics* (SiHoLS 106); Zwartjes 2011, *Portuguese Missionary Grammars in Asia, Africa and Brazil 1550-1800* (SiHoLS 117, with an appendix on lexicography). [C: https://en.wikipedia.org/wiki/Even_Hovdhaugen ; https://lwc1.benjamins.com/catalog/sihols.117.toc] Focus is grammars and missionary-quality lexicography, not travellers' lists; useful for the "collector type" contrast (missionary vs. mariner).
- Leopold, *The Prix Volney* (Kluwer, 1999) — on comparative-vocabulary culture c.1800 [C: https://link.springer.com/book/9789401098762]; Pallas/Catherine II *Linguarum totius orbis vocabularia comparativa* (1786-89) as a questionnaire-driven list corpus [C: same results].
- Harvey 2015, *Native Tongues: Colonialism and Race from Encounter to the Reservation* (Harvard) — Jefferson/Barton/Gallatin vocabulary forms. [C: https://muse.jhu.edu/article/610633] Gray 1999 *New World Babel* [I]; Gray & Fiering 2000 [C above].
- Errington 2008, *Linguistics in a Colonial World* (Blackwell). [C: https://macmillanreport.yale.edu/node/95]
- Fernández Rodríguez 2023, "Language, Science and Globalization in the Eighteenth Century", *Berichte zur Wissenschaftsgeschichte* [C: https://onlinelibrary.wiley.com/doi/10.1002/bewi.202200040 — title/venue only; page 403'd].
- Cromohs 25/2022 piece on early-modern scientific travellers' vocabularies starting from ~13 words (body parts, eat, drink) and growing [C: https://oajournals.fupress.net/index.php/cromohs/article/download/13822/13146/26747 — author/title not verified]. Relevant to category (3): body-part-first elicitation was a recognised protocol.
- Interactional-word universals: Dingemanse, Torreira & Enfield 2013, "Is 'Huh?' a universal word?", *PLoS ONE* 8(11): e78273 [C: https://pmc.ncbi.nlm.nih.gov/articles/PMC3832628/]. Gives a principled reason why repair initiators / "what?" forms would surface across unrelated lists — useful baseline for category (1).
- Enfield's body-part elicitation guide (MPI) — modern methodological discussion of body-part ostension [C: https://pure.mpg.de/rest/items/item_60128/component/file_60129/content].

**Gap I could not fill:** I found no published discussion that treats *possessive-prefixed body-part entries* (Algonquian *n-*/'my', Oceanic suffixed possessors) as a systematic collector artifact across sources [searched; nothing found]. Americanists know it informally (e.g. Algonquian body-part words all beginning with *n-* 'my' [C: http://www.native-languages.org/algonquin_possession.htm]), but I could not find a citable study. This is a genuine opening for category (3).

---

## B. The famous anecdotes and their status

| Anecdote | Popular claim | Scholarly status | Sources |
|---|---|---|---|
| **kangaroo** (Cook/Banks 1770) | Guugu Yimithirr for "I don't understand" | **Debunked.** *gangurru* = a large grey/black kangaroo species; Roth tried to correct the legend in 1898; Haviland's fieldwork (c.1972, publ. 1974) confirmed. A real *related* error survives: Cook/Banks took a species term as generic, and the First Fleet then used the Guugu Yimithirr word at Sydney, where it was not understood — i.e. a **transported-vocabulary/contact** artifact rather than an interactional one. | [C] https://en.wikipedia.org/wiki/Kangaroo ; https://www.macquariedictionary.com.au/the-origin-of-kangaroo-getting-to-the-bottom-of-an-australian-furphy/ ; https://www2.sl.nsw.gov.au/archive/discover_collections/history_nation/indigenous/vocabularies/index.html ; https://languagehat.com/kangaroo/ |
| **Yucatán** | Maya "I don't understand you" | **Legend, multiple competing versions, all doubtful.** Variants attributed to Cortés (1519 letter), Motolinía ("Tectetán"), Gómara (1554), and Landa ("ci u than", 'they say it'). Commentators note no good 16th-c. Yucatec match. The *proliferation of versions* is itself evidence that "I don't understand → name" was a stock Spanish trope. I did not confirm a specific Restall passage on this [I: Restall's *Seven Myths* (2003) or *Maya Conquistador* (1998) may discuss it]. | [C] https://en.wikipedia.org/wiki/Yucatan ; https://sacred-texts.com/nam/maya/ybac/ybac06.htm ; https://www.etymologynerd.com/blog/where-is-the-yucatan ; https://www.straightdope.com/columns/read/491/whats-the-origin-of-kangaroo-court |
| **indri** (Sonnerat 1782) | Malagasy *indry* 'there it is!' | **Doubted.** Sonnerat knew the animal well (described, figured, apparently kept one), making a pointing error implausible; *endrina* is an attested Malagasy name. Key cite: Dunkel, Zijlstra & Groves 2012, "Giant rabbits, marmosets, and British comedies: etymology of lemur names, part 1", *Lemur News* 16: 65ff. | [C] https://en.wikipedia.org/wiki/Indri ; https://www.etymonline.com/word/indri |
| **Canada** (Cartier 1535) | Iroquoian *kanata* 'village' misread as country name | **Broadly accepted** as a scope error (common noun → proper name), not an interactional error. Cartier's own Stadaconan vocabulary glosses *canada* as 'town' [I: in the Cartier relation vocabulary]. | [C] https://en.wikipedia.org/wiki/Name_of_Canada ; https://www.canada.ca/en/canadian-heritage/services/origin-name-canada.html ; https://www.historymuseum.ca/blog/canada-the-complicated-history-of-a-name |
| **papālagi** (Samoan 'European', 'sky-bursters') | folk etymology | Re-examined by Tent & Geraghty ("exploded myth"). | [C] https://researchers.mq.edu.au/en/publications/exploding-sky-or-exploded-myth-the-origin-of-pap%C4%81lagi/ |
| Others to check [I] | Nome ("Name?" on a map), Lake Titicaca, llama ("¿cómo se llama?"), Luzon/"Philippines" stories, Tierra del Fuego | Mostly popular folklore; not verified. |

**Takeaway for framing:** the iconic "I don't know → name" stories are mostly *false* or unprovable, and specialists treat them as a colonial trope (Straight Dope / Macquarie summarise this; Haviland is the scholarly anchor). That is a selling point: the paper can ask whether the *genuine* rate of interactional forms in lists is high or low, replacing anecdote with measurement. Conversely, the *documented* artifacts are less colourful: pidgin/jargon contamination (Koch, Troy, Goddard, Gibbs/Scouler, Drechsel), transported vocabularies (kangaroo at Sydney), species/generic scope errors (kangaroo, Canada), and copying chains (Pigafetta, Bausani).

---

## C. Venues

History of linguistics:
- *Historiographia Linguistica* (Benjamins) — the flagship; publishes on colonial vocabularies (e.g. 2022 Molina/Olmos Nahuatl vocabulary paper [C: https://lwc1.benjamins.com/catalog/hl.00109.jac]). Good fit if framed historically.
- *Language & History* (Henry Sweet Society, T&F) [I].
- *History of Linguistics / Beiträge zur Geschichte der Sprachwissenschaft* [I].
- Book series: *Studies in the History of the Language Sciences* (Benjamins) [C: https://www.degruyterbrill.com/serial/jbpshls-b/html].

Historical / contact linguistics:
- *Journal of Pidgin and Creole Languages* — natural home for categories (4)/(5) (Drechsel has published there [C: https://lwc1.benjamins.com/catalog/jpcl.22.2.03dre]).
- *Journal of Historical Sociolinguistics* (De Gruyter) [I].
- *Diachronica*; *Language Dynamics and Change* (Brill) — if the quantitative modelling is central [I].
- *Anthropological Linguistics*; *Language Documentation & Conservation* (LD&C; open access, interest in legacy materials) [I for fit].
- Regional: *Oceanic Linguistics*, *Australian Journal of Linguistics*, *International Journal of American Linguistics* — fit for a region-focused spin-off.

History of science / knowledge:
- *Isis*, *BJHS*, *History of Science*, *Berichte zur Wissenschaftsgeschichte*, *Journal of the History of Ideas*, *Itinerario* (European expansion) [I for fit; Berichte confirmed as publishing on language & science 18th c.].
- *Cromohs* (open access early-modern historiography) [C link above].

Digital humanities / computational:
- *Digital Scholarship in the Humanities* (publishes on EEBO [C: https://academic.oup.com/dsh/advance-article/doi/10.1093/llc/fqaf086/8316931]), *Journal of Cultural Analytics*, *Digital Humanities Quarterly*, *Journal of Open Humanities Data* (for the dataset) [I].
- CL venues: LaTeCH-CLfL workshop (ACL), SIGTYP, LChange workshop [I].
- Cross-over: *Humanities and Social Sciences Communications*, *PNAS Nexus*, *Science Advances* if the result is general and striking [I].

Suggested split: a methods/dataset paper (DSH or JOHD + LaTeCH) and a substantive paper (Historiographia Linguistica or JPCL, or a history-of-science journal if the collector-type/contact-duration argument is foregrounded).

---

## D. Judgment on novelty and must-cite list

**Novelty: genuinely novel at the level of design, not at the level of phenomena.** Every artifact type is individually known and has case-study literature; what does not appear to exist is (a) a coded taxonomy applied uniformly across hundreds of lists from different regions and centuries, (b) *rates*, and (c) regression of those rates on collector type, contact duration, region and date. The most aggregate-flavoured precedents are Drechsel (claims many Polynesian lists are pidgin, but argued qualitatively), Hair (serial but list-by-list), Troy (pidgin reconstruction from many sources), Simpson (one loan across many sources), and CHIRILA's per-source reliability ratings. None reports artifact rates. Caveat: my search was web-based; JSTOR/Benjamins full-text could reveal a regional quantitative study (most likely in Australian or Pacific linguistics, e.g. a thesis using CHIRILA or Curr's *The Australian Race*). Recommend a targeted check of: Australian Journal of Linguistics, Pacific Linguistics catalogue, and Historiographia Linguistica indexes for "reliability", "early sources", "vocabulary", 1990-2026.

**Risks reviewers will raise**
1. Gold standard: identifying an "error" requires a modern reference lexicon; historical change and dialect differences inflate apparent error rates (Koch and Haviland both handle this by careful re-elicitation). Need a confidence tier per judgment.
2. Folk etymologies are mostly false — so do not use kangaroo/Yucatán as evidence for category (1); use them as the foil.
3. Drechsel's pidgin thesis is contested; categorising a whole list as "intermediary language" needs explicit, replicable criteria.
4. Copying chains (Pigafetta reprinted for centuries; Bausani) mean lists are not independent observations — model stemmatics/dependence.
5. Printed vs. manuscript selection bias (EEBO covers print to 1700; Cook/Dawes material is manuscript).

**Must cite and engage (core)**
- Haviland 1974 (Oceania) — re-elicitation model; kangaroo.
- Koch 2016 (Ngarigu) and the *Language, Land & Song* volume; Simpson 2016; Troy 1994 — Australian contact-layer philology.
- Bowern's CHIRILA (and its reliability ratings).
- Drechsel 2014 — whole-list-as-pidgin thesis.
- Bakker 1989 (+ Basque-Icelandic and Mi'kmaq loan papers).
- Goddard 1995/1997/2000 — Pidgin Delaware; Gray & Fiering 2000.
- Gibbs 1863 / Scouler and Thomason on Chinook Jargon contamination.
- Clark 1979; Baker & Mühlhäusler 1996 — Pacific jargon lexicon.
- Dalgado 1913 — Portuguese loan lexicon; Tent & Geraghty 2003.
- Hair (Africa Encountered) — West African early vocabularies.
- Bausani 1960 / Pigafetta scholarship; Hoogervorst 2024 — Malay intermediary lists.
- Dunkel, Zijlstra & Groves 2012 (indri); Restall/Landa sources (Yucatán).
- Zwartjes 2011, Hovdhaugen 1996, Zwartjes & Hovdhaugen 2004 — missionary linguistics as the "collector type" contrast.
- Errington 2008; Harvey 2015 — history-of-knowledge framing.
- Dingemanse et al. 2013 — interactional universals baseline.
- Lexibank/ASJP and automated borrowing detection (List et al.) — methodological neighbours to distinguish from.

**Names the brief mentioned that I could not confirm a directly relevant publication for (check manually):** Ken Hale on the kangaroo myth (the debunking literature credits Roth 1898 and Haviland; I found no Hale piece); "Rhodes" on early Pacific vocabularies; Pawley on the reliability of early Pacific vocabularies (Pawley's work is comparative Oceanic/TNG; a specific early-vocabulary reliability paper not found); Florey on historical-list reliability; Nash on early-source reliability (Nash's bibliography page is https://www0.anu.edu.au/linguistics/nash/papers/ — check there); Lynch on Forster/Cook Vanuatu lists (likely exists, not confirmed).
