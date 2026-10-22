# MDZ (Bayerische Staatsbibliothek) pass

## How the search works
- Site full-text search is a JSON API: `https://www.digitale-sammlungen.de/api/search?query=<q>&handler=simple-fulltext&ocrContext=1&pageSize=50&startPage=N` (handlers: simple-all, simple-fulltext, simple-metadata). Returns docs + OCR snippets with page ids (bsbXXXXXXXX_NNNNN). Found in /static/assets/api-*.js.
- Metadata: `/api/metadata/<bsbID>`. Per-page hOCR: `https://api.digitale-sammlungen.de/ocr/<bsbID>/<page>` (linked as seeAlso from IIIF v2 canvas). Within-volume search: `https://api.digitale-sammlungen.de/iiif/services/search/v1/<bsbID>?q=`.
- Manuscripts (Cod.hisp., Cod.gall., Cod.sin., Cod.or., Cod.icon.) are in the same index, searchable via handler=simple-metadata; most have no OCR. Metadata queries for vocabulario/vocabulaire/Wörterbuch in Cod.* returned nothing new (Cod.hisp. 39 Portuguese-Latin/German vocab only).
- No bot checks encountered.

## Queries (fulltext, pre-1900 hits kept; ~5,000 snippets triaged)
German: "Verzeichniß/Verzeichniss einiger Wörter", "Wörter ihrer Sprache", "in ihrer Sprache heißt/heisst", "Zahlwörter der", "Sprachprobe der", "Wörterverzeichniß der", "Proben ihrer Sprache", "einige Wörter aus der Sprache", "Wörter der Sprache der", "nennen sie in ihrer Sprache", "Wörterverzeichniß der Sprache", "kleines Wörterverzeichniß", "Verzeichniß einiger Wörter aus der", "einige Wörter ihrer Sprache", "Wörter aus ihrer Sprache", "zählen sie also", "Sprache der Wilden/Neger/Mohren", "Malabarische Wörter", "Grönländische Wörter", "Proben der Sprache", "Zahlwörter der Neger".
Ethnonyms: Sprache der Botocuden, Puris, Coroados, Camacans, Patachos, Guaycuru, Mbayas, Abiponer, Mocobier, Lules, Vilelas, Charruas, Feuerländer, Pescherähs, Kamtschadalen, Koriäken, Jukagiren, Kotten, Arinen, Hottentotten, Buschmänner, Tasmanier, Guanchen; Wörter der Guanchen.
Latin/Romance: "vocabula linguae", "lingua eorum vocant" (0), "lingua Guaranica", "lingua Brasilica", "ita numerant" (noise), "quelques mots de leur langue", "mots de la langue des", "vocabulaire de la langue", "petit vocabulaire", "alcune parole della lingua", "vocabolario della lingua (dei)", "nella lor lingua chiamano", "algunas palabras de su lengua", "en su lengua llaman", "woorden van hunne taal".

## Results
- NEW WITNESS: Dudley, Arcano del mare draft, Cod.icon. 140, img 159 - Trinidad/Guiana word list in Italian (obscure; English version known via Warner 1899).
- Ehrmann 1792 Wolof/Fula/Mandinka list - known (Glottolog).
- Lead, not verified: review in Jenaische ALZ 1815 (bsb10502140 p.183) of Labarthe, Reise nach der Küste von Guinea (Leipzig: Joachim 1805, tr. Bergk) notes "S. 61 ein fantinsches Wörterverzeichniß" (Amaku/Gold Coast). The 1803 Weimar German edition on MDZ (bsb10465717) did not show the list at the expected place; the 1805 Bergk edition was not found on MDZ. Labarthe is not in Glottolog Akan refs. Worth checking French original (Voyage à la côte de Guinée, 1803).
- Lead, not verified: Gothaische gelehrte Zeitungen 1789 (bsb10502273 p.617) reviews a French-American travel compilation incl. "Verzeichniß einiger Wörter aus der Sprache der Wilden am [?]" - source book not identified.
- Known/skip: Lesseps Kamchadal 1791; Molina Chilean 1786; Glas Guanche (1804 Ger.); Klaproth Koibal/Motor 1816; Shaw Shawia 1765; Russian discoveries "Meutier" (Aleut) 1783; Pyrard Maldives 1619; Gumilla Betoye; Kotzebue 1832; Cook voyages (German eds.); Mithridates.
