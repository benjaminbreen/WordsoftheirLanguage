import type { APIRoute } from "astro";
import { tables, fold } from "../../lib/data";

// Search index, fetched lazily by /search. Compact rows; table metadata once.
export const GET: APIRoute = () => {
  const T = tables.map((t) => ({ id: t.id, lang: t.language.name, book: t.book.short, year: t.book.printed,
    pages: t.pages.map((p) => [p.sm, p.w, p.h]) }));
  const rows = tables.flatMap((t, ti) => t.entries.map((e) => [ti, e.n, e.form, e.gloss, fold(e.form), fold(e.gloss),
    (e.concepts || []).map((c) => c.toLowerCase()).join("|"),
    e.box && !e.box.approx ? [e.box.page, e.box.x, e.box.y, e.box.w, e.box.h] : 0, e.note ? 1 : 0]));
  return new Response(JSON.stringify({ v: 1, tables: T, rows }), { headers: { "Content-Type": "application/json" } });
};
