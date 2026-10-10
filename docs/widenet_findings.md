# Wide-net search for undescribed early modern word lists (2026-10-04)

Sources searched (raw results in `data/work/widenet/*.jsonl`, query logs in `*_log.md`):
Evans-TCP + ECCO-TCP (detector, `src/detect_tcp.py`); Internet Archive full text; Gallica; manuscript
catalogues (Kalliope, Wellcome, Royal Society, British Library, Cambridge UL); Iberian archives (via AGI
studies; PARES was down); a target-first pass over the Glottolog gap list; and a structural scan of all
4.79M VOC pages (`src/voc_structural.py`). 41 verified items: 19 obscure, 22 known. Nothing is "new" until
a specialist confirms it; "obscure" = we found no linguistic citation.

Blocked or not reached: HathiTrust (Cloudflare check), Gallica page text (ALTCHA), PARES (502), Real
Biblioteca, Calames, Bodleian, BnF Archives et manuscrits, Leiden. None of these were bypassed.

## Shortlist (ranked)

1. **Sydney language (Dharug/Eora) words supplied by Rev. Samuel Marsden**, in an anonymous Malay
   vocabulary, Cambridge UL, BFBS/BSMS 338 (1800-1825; 39 ff., 4 columns). Catalogue note (ff. 26v-27r):
   "The parallel words in the dialect of Botany Bay or Sidney Town were given me by ... the Rev. S.
   Marsden ... He can converse with the natives"; it also says David Collins was indebted to Marsden for
   "his vocabulary of the native words". Not in Steele's 2005 thesis on the Sydney sources (which mentions
   Samuel Marsden only to distinguish him from William Marsden) or in Troy 1993. Word count unknown;
   record verified, pages not seen. https://archivesearch.lib.cam.ac.uk/repositories/2/archival_objects/228629
2. **Meriam Mir (Murray Island, Torres Strait), 1834.** Anonymous naval officer, "Some account of the
   natives of Murray's Island", *United Service Journal* 1834; 70-100 words, about a decade before Jukes
   (1847), the earliest source Glottolog lists. https://archive.org/details/in.ernet.dli.2015.21628
3. **AGI Indiferente 1342A, n.1 (Catherine II/Pallas questionnaire returns):** Costa Rica 1789 list with
   Cabécar, Viceyta (Bribri) and an unidentified **"Lean-Mulia"** column (fols. 278v-289r); a separate
   **Térraba** list (1789); a **Sáliba dictionary** (c. 1790). Lost (unverified): 1789 New Granada lists in
   Guamo, Otomaco, Taparita, Jayuya, Motilón, possibly in the Real Biblioteca, Madrid.
4. **Aussant, *Vocabulaire françois, anglois, portugais de l'Inde, persan, maure et bengale*,
   Chandernagore 1782** (BnF Indien 731), about 3,700 words in 6 columns. Pages viewed: the Indo-Portuguese
   column has creole features (*fazé cara*). Known to historians of the BnF Indian manuscripts; apparently
   unused as a source for Bengal Indo-Portuguese creole. https://gallica.bnf.fr/ark:/12148/btv1b10462862q
5. **Strange expedition, "Additions to Capt. Cook's Vocabulary of the Nootka Sound Language", 1786**,
   BL IOR/H/800, pp. 147-61. Status of edition unclear. https://searcharchives.bl.uk/catalog/040-000004910
6. **Uab Meto (Timor), van Hogendorp 1779** (Verh. Bataviaasch Genootschap 1; French translation in
   *Annales des voyages* 6, 1809): numerals and about 100 nouns. https://archive.org/details/annalesdesvoyag06unkngoog
7. **Creek (Muskogee) words in John Pope, *A Tour* (Richmond 1792)**, about 45 words collected 1791;
   Pilling not checked.
8. Smaller manuscript leads: Hecquard, Abure vocabulary, Grand-Bassam 1850 (BnF Africain 6); French-Mohawk
   dictionary attributed to La Galissonnière (BnF Américain 17); English-Arawak vocabulary, 447 ff., 1844
   (Cambridge UL BFBS/BSMS 74); "The Malyan tongue" in Sloane MS 2117 (17th c.); Kiernander on Madagascar
   (Francke Foundations, AFSt/M 2 D 35 : 7); Russian-English-Yupik notebook, St Michael 1850-51 (Wellcome
   MS Amer.108); Quechua-Spanish drafts on the backs of indulgences, 1766 (CUL BSMS 420).

## Negative results worth recording
- VOC archive: no copied word lists in 4.79M pages (structural scan); the archive mentions vocabularies
  (see `voc_register_findings.md`) but almost never copies them.
- Evans/ECCO: treaty records, captivity narratives, sermons and almanacs yielded no word lists.
- Gap-list pass (33 of 60 targets searched): dead ends confirmed for Tonocoté, Guale, Payaya, Aranama,
  Yamasee, Meherrin, Erie, Etchemin, Michigamea and others.
- Method: generic phrase searches drown in known compilations (Hervás, Adelung, Klaproth); periodical-title
  restriction and manuscript catalogues were the only productive routes.

## Round 2 (2026-10-10): old bibliographies read in reverse; TNA Discovery
Files: `data/work/biblio/` (Ludewig 1858, Vater/Jülg 1847, Marsden 1796/1827), `data/work/discovery/`.
Helper: `src/glotto_refs.py` (Glottolog references per language, for novelty checks).

- Meriam Mir check: Wilson 1835 (cited by Glottolog) describes an 1822 visit from memory, with none of the
  1834 list's words; the 1834 *United Service Journal* list is a separate record, earlier than Jukes 1847.
- Discovery: RGS JMS/13/27, Mate Vallack's Port Essington vocabulary (1840, 9 pp.), sent by Owen Stanley,
  recommended for publication, never printed; not in Glottolog's Iwaidja references.
  Lancashire Archives DDHK 9/2/13 (c. 1662): "Malayan numbers and phrases" and "Cambrian speech used in
  America" on a reused wrapper. TNA C 106/170-171: Scattergood's Chinese and Spanish commercial
  vocabularies (1698-1719). Admiralty Library MSS 23 etc.: HMS Herald journal with Pacific vocabularies
  (1852-55). UKHO LP1857 D/289: De Horsey and Montgomerie's Columbia River vocabulary (1848).
- Marsden 1827 manuscripts (probably SOAS Marsden Collection, unverified): Palauan-Malay-English
  vocabulary; English-Moroccan Arabic-Shilha vocabulary via Consul Matra, Tangier 1788; d'Entrecasteaux
  expedition vocabularies of Van Diemen's Land and Tonga (1793); vocabularies of Assam dialects.
  Neither Marsden catalogue mentions Rev. Samuel Marsden.
- Ludewig 1858, lost manuscripts: Ucayali vocabularies (Conibo, Setebo, Campa) from the Chaumette des
  Fossés sale, Paris 1842 (nos. 581-584); Siona "Diccionario y Doctrina en Lengua Zeona" (416 pp.) owned
  by Joaquín Acosta; Michilimackinac French-Algonquin vocabulary 1740-48 (582 pp.) owned by Hugh Ramsay.
- Vater/Jülg 1847: almost no manuscripts; minor printed orphans (Balfour 1844 Bauria etc.; Brumund on Aru;
  Kilham's "Appa" and "Rungo").
