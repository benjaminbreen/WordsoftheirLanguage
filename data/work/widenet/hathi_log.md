# hathi log (2026-10-04)

Result: BLOCKED, no rows.

- curl to babel.hathitrust.org/cgi/ls (full-text search, phrase query): Cloudflare "Performing security verification" challenge page.
- Built-in browser pane, same URL: stuck on the Cloudflare verification page after waiting; not bypassed (bot checks are off-limits).
- catalog.hathitrust.org/api/volumes and Search/Home: 403 / Cloudflare challenge.

No queries could run, so hathi.jsonl is empty. Options: the user searches HathiTrust in their own browser and passes on item IDs (pt?id= pages could then be checked, though they are probably also behind the challenge), or use Internet Archive / Google Books full text instead (many of the same 18th-19th c. periodicals are there).
