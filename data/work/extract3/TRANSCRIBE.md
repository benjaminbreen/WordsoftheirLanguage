# Transcribing a printed or manuscript word list for the site

1. Locate the list pages. Internet Archive items: OCR in the item's *_djvu.txt / *_djvu.xml (file names may
   differ from the item id: check https://archive.org/metadata/<id>); page images via
   https://iiif.archive.org/iiif/<id>$<leaf>/full/1600,/0/default.jpg (leaf = n in /page/n<leaf>).
2. Download the list pages to the scratchpad and READ EVERY IMAGE. Transcribe from the images (OCR only as a
   guide), keeping printed/written spelling, accents and punctuation; every entry in order.
3. Write data/work/extract3/<key>.entries.csv with columns exactly:
   n,section_heading,gloss_as_printed,form_as_printed,form_language_label_as_printed,note
   gloss = the European-language gloss as printed; form = the non-European form; section_heading = printed
   headings over the list or sub-lists; form_language_label_as_printed = the language name the source gives
   when a list mixes languages (e.g. two columns); note only for real transcription problems.
4. Write data/work/extract3/<key>.meta.json: {ia or source_url, leaves:[...], title_as_printed, author,
   journal/volume/pages or book imprint, year_printed, heading_as_printed (verbatim sentence or heading
   introducing the list), place, heard (date of collection if stated), collector, about (ONE plain factual
   sentence on where the words came from, using facts stated in the source; no commentary)}.
Return: entries count, leaves, heading, problems.
