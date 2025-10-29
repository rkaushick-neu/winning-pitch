import { apiGet, apiGetText, apiPostForm } from "./client";
import type { MarkdownFile, IngestResponse } from "../types";

// GET all markdown files (ids & display names)
export async function getMarkdownList(): Promise<MarkdownFile[]> {
  // You mentioned: "GET request to get all the .md files present in /data/markdown"
  const res = await apiGet<{ markdowns: MarkdownFile[]; count: number }>("/api/markdowns");
  return res.markdowns; // extract the list from the response
}

// GET a single markdown by id
export function getMarkdownById(id: string): Promise<string> {
  // You mentioned: GET /markdown/{markdown_id} returns raw markdown text
  return apiGetText(`/api/markdowns/${encodeURIComponent(id)}`);
}

// POST PDF to /ingest (multipart/form-data)
export function ingestPitchDeck(file: File): Promise<IngestResponse> {
  const form = new FormData();
  form.append("file", file);
  return apiPostForm<IngestResponse>("/api/ingest", form);
}