import type { APIRoute } from "astro";
import { tables, byId } from "../../../lib/data";

export function getStaticPaths() {
  return tables.map((t) => ({ params: { id: t.id } }));
}
const cell = (v: unknown) => {
  const s = v == null ? "" : String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
export const GET: APIRoute = ({ params }) => {
  const t = byId[params.id!];
  const head = ["table_id", "entry", "form_as_printed", "gloss_as_printed", "section_as_printed", "column", "concepts",
    "page", "x", "y", "w", "h", "position_estimated", "note_kind", "note", "note_compare", "language", "book", "printed", "tcp_id"];
  const lines = [head.join(",")];
  for (const e of t.entries) {
    lines.push([t.wtl, e.n, e.form, e.gloss, e.section, e.col, (e.concepts || []).join(";"),
      e.box ? e.box.page + 1 : "", e.box?.x, e.box?.y, e.box?.w, e.box?.h, e.box?.approx ? "yes" : "",
      e.note?.label, e.note?.text, e.note?.compare, t.language.name, t.book.short, t.book.printed, t.book.tcp].map(cell).join(","));
  }
  return new Response("﻿" + lines.join("\n") + "\n", { headers: { "Content-Type": "text/csv; charset=utf-8" } });
};
