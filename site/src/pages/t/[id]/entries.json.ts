import type { APIRoute } from "astro";
import { tables, byId } from "../../../lib/data";

export function getStaticPaths() {
  return tables.map((t) => ({ params: { id: t.id } }));
}
export const GET: APIRoute = ({ params }) => {
  const t = byId[params.id!];
  return new Response(JSON.stringify(t, null, 1), { headers: { "Content-Type": "application/json; charset=utf-8" } });
};
