// Read-only access to the pipeline's output (src/data/*.json). The pipeline is the only writer.

export interface Box { page: number; x: number; y: number; w: number; h: number; approx?: boolean }
export interface Note { kind: string; label: string; text: string; compare: string | null; checked: boolean }
export interface Entry {
  n: number; form: string; gloss: string; section?: string; col?: string;
  concepts?: string[]; box?: Box; note?: Note;
  p?: number; text?: string; trans?: string; modern?: { name: string; where: string; ml: string; conf: string };
}
export interface Page { leaf: number; w: number; h: number; sm: string; lg: string; href?: string; label?: string }
export interface Candidate { name: string; db: string; family: string; path: string[]; z: number; n: number }
export interface Identification {
  status: "resolved" | "abstain"; path: string[]; support: number[]; concepts: number; excluded: string[];
  leading: { name: string; family: string; z: number } | null;
  candidates: Candidate[]; evidence: { concept: string; form: string; ref: string; d: number }[];
}
export interface Table {
  schema: number; id: string; wtl: string; heading: string | null; headings: string[];
  language: { name: string; glottocode: string | null; family: string | null; path: string[]; labels: string[] };
  region: string;
  book: { short: string; title: string | null; author: string; printed: number; imprint: string | null; tcp: string; cover: string; kind?: string };
  provenance: { collector: string; place: string; heard: string };
  scan: { ia: string; url: string; holder: string | null; note: string | null; rights: string; source?: string };
  transcription?: string;
  pages: Page[]; entries: Entry[]; identification: Identification | null;
  stats: { entries: number; notes: number; located: number };
  partial: string | null; relation: { kind: string; table: string; text: string } | null;
}

const mods = import.meta.glob<{ default: Table }>("../data/tables/*.json", { eager: true });
export const tables: Table[] = Object.values(mods).map((m) => m.default).sort((a, b) => a.book.printed - b.book.printed);
export const byId: Record<string, Table> = Object.fromEntries(tables.map((t) => [t.id, t]));

export const REGIONS = ["North America", "Caribbean & South America", "Arctic & North", "Africa & Indian Ocean", "Asia", "Australia & Pacific"];

export const totals = {
  tables: tables.length,
  entries: tables.reduce((s, t) => s + t.stats.entries, 0),
  languages: new Set(tables.map((t) => t.language.name)).size,
  books: new Set(tables.map((t) => t.book.tcp)).size,
  first: Math.min(...tables.map((t) => t.book.printed)),
  last: Math.max(...tables.map((t) => t.book.printed)),
};

export const cover = (t: Table, size: 360 | 720 = 360) => `/covers/${t.book.cover}-${size}.webp`;

/** CSS for a box cut from a page image: the element shows exactly the printed line. */
export function cropStyle(p: Page, b: Box, padX = 0.004, padY = 0.002) {
  const x = Math.max(0, b.x - padX), y = Math.max(0, b.y - padY);
  const w = Math.min(1 - x, b.w + 2 * padX), h = Math.min(1 - y, b.h + 2 * padY);
  const ratio = (w * p.w) / (h * p.h);
  const px = w >= 1 ? 0 : (x / (1 - w)) * 100, py = h >= 1 ? 0 : (y / (1 - h)) * 100;
  return `background-image:url(${p.sm});background-size:${(100 / w).toFixed(3)}% auto;background-position:${px.toFixed(3)}% ${py.toFixed(3)}%;aspect-ratio:${ratio.toFixed(4)}`;
}

/** Early-modern spelling folding, shared with the search page (keep in sync with search.ts). */
export function fold(s: string) {
  return (s || "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .replace(/ſ/g, "s").replace(/vv/g, "w").replace(/v/g, "u").replace(/j/g, "i").replace(/y/g, "i")
    .replace(/ck/g, "k").replace(/ph/g, "f").replace(/[^a-z0-9 ]/g, "");
}

/** concept -> occurrences across tables (first form per table). Copies of other tables are left out,
 *  so a word recorded once is not counted twice. */
export const conceptIndex: Record<string, { table: string; n: number; form: string; lang: string; year: number }[]> = {};
for (const t of tables) {
  if (t.relation?.kind === "copied-from") continue;
  const seen = new Set<string>();
  for (const e of t.entries) for (const c of e.concepts || []) {
    if (seen.has(c)) continue;
    seen.add(c);
    (conceptIndex[c] ||= []).push({ table: t.id, n: e.n, form: e.form, lang: t.language.name, year: t.book.printed });
  }
}

export const conceptLabel = (c: string) => c.toLowerCase().replace(/\s*\(.*?\)/g, "");

export function citation(t: Table, n?: number) {
  const where = n ? `, entry ${n}` : "";
  return `“${t.language.name} vocabulary${where},” in ${t.book.author}, ${t.book.short} (${t.book.printed}). ` +
    `Wordes of their Language, ${t.wtl}${n ? "." + n : ""}.`;
}
