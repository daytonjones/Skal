import { apiFetch } from "../lib/apiFetch";
import type {
  Paginated,
  Batch,
  BatchInput,
  TastingNote,
  TastingNoteInput,
  BottleConsumption,
  BottleConsumptionInput,
  BatchImage,
} from "./types";

export function listBatches(page = 1): Promise<Paginated<Batch>> {
  return apiFetch<Paginated<Batch>>(`/api/v1/batches/?page=${page}`);
}

export function getBatch(id: number): Promise<Batch> {
  return apiFetch<Batch>(`/api/v1/batches/${id}/`);
}

export function createBatch(input: Partial<BatchInput>): Promise<Batch> {
  return apiFetch<Batch>("/api/v1/batches/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateBatch(id: number, input: Partial<BatchInput>): Promise<Batch> {
  return apiFetch<Batch>(`/api/v1/batches/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteBatch(id: number): Promise<void> {
  return apiFetch<void>(`/api/v1/batches/${id}/`, { method: "DELETE" });
}

export function listTastingNotes(batchId: number): Promise<Paginated<TastingNote>> {
  return apiFetch<Paginated<TastingNote>>(`/api/v1/tasting-notes/?batch=${batchId}`);
}

export function createTastingNote(input: TastingNoteInput): Promise<TastingNote> {
  return apiFetch<TastingNote>("/api/v1/tasting-notes/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function listBottleConsumption(batchId: number): Promise<Paginated<BottleConsumption>> {
  return apiFetch<Paginated<BottleConsumption>>(`/api/v1/bottle-consumption/?batch=${batchId}`);
}

export function createBottleConsumption(input: BottleConsumptionInput): Promise<BottleConsumption> {
  return apiFetch<BottleConsumption>("/api/v1/bottle-consumption/", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function listBatchImages(batchId: number): Promise<Paginated<BatchImage>> {
  return apiFetch<Paginated<BatchImage>>(`/api/v1/batch-images/?batch=${batchId}`);
}

export function uploadBatchImage(batchId: number, uri: string, caption: string): Promise<BatchImage> {
  const form = new FormData();
  form.append("batch", String(batchId));
  form.append("caption", caption);
  const filename = uri.split("/").pop() ?? "photo.jpg";
  const match = /\.(\w+)$/.exec(filename);
  const ext = match ? match[1] : "jpg";
  form.append("image", {
    uri,
    name: filename,
    type: `image/${ext === "jpg" ? "jpeg" : ext}`,
  } as unknown as Blob);
  return apiFetch<BatchImage>("/api/v1/batch-images/", {
    method: "POST",
    body: form,
  });
}
