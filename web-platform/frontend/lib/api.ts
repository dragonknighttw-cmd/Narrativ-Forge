const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(base + path, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = await response.json();
      message = typeof body.detail === "string" ? body.detail : body.detail?.message ?? message;
    } catch {}
    throw new Error(message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

async function idempotentRequest<T>(storageKey: string, path: string, init: RequestInit): Promise<T> {
  const key = typeof window === "undefined"
    ? crypto.randomUUID()
    : localStorage.getItem(storageKey) ?? crypto.randomUUID();
  if (typeof window !== "undefined") localStorage.setItem(storageKey, key);
  const result = await request<T>(path, {
    ...init,
    headers: { ...(init.headers ?? {}), "Idempotency-Key": key },
  });
  if (typeof window !== "undefined") localStorage.removeItem(storageKey);
  return result;
}

export type Idea = { id: string; title: string; concept?: string | null; category?: string | null; hook?: string | null; content_warning?: string | null; status: string; created_at: string };
export type Series = { id: string; title: string; description?: string | null; status: string; created_at: string };
export type Season = { id: string; series_id: string; season_number: number; title?: string | null; created_at: string };
export type Episode = { id: string; public_id: string; series_id: string; season_id?: string | null; episode_number: number; title: string; category?: string | null; synopsis?: string | null; target_duration_seconds: number; actual_duration_seconds?: number | null; status: string; current_step: string; row_version: number; created_at: string; updated_at: string };
export type Script = { id: string; episode_id: string; version: number; title?: string | null; content: string; status: string; is_current: boolean; row_version: number; created_at: string; updated_at: string };
export type EpisodeUpdateInput = Partial<Omit<Episode, "id" | "row_version" | "created_at" | "updated_at">> & { expected_row_version: number };
export type Scene = { id: string; episode_id: string; script_id?: string | null; scene_number: number; purpose: string; description?: string | null; dialogue?: string | null; duration_seconds?: number | null; created_at: string; updated_at: string };
export type Asset = { id: string; episode_id: string; scene_id?: string | null; asset_type: string; original_filename: string; storage_provider: string; local_path?: string | null; mime_type: string; file_size_bytes: number; version: number; copyright_status: string; is_final: boolean; status: string; created_at: string };
type UploadPart = { part_number: number; size_bytes: number; checksum_sha256: string };
type UploadSession = {
  id: string;
  episode_id: string;
  asset_type: string;
  mime_type: string;
  expected_size: number;
  chunk_size: number;
  scene_id?: string | null;
  status: string;
  parts: UploadPart[];
  asset?: Asset;
};
class UploadResponseError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
  }
}
export type CreateSceneInput = { scene_number: number; script_id?: string; purpose: string; description?: string; dialogue?: string; duration_seconds?: number };
export type ProcessingJob = { id: string; episode_id: string; job_type: string; status: string; progress: number; retry_count: number; input_asset_id?: string | null; output_asset_id?: string | null; error_code?: string | null; error_message?: string | null; created_at: string; completed_at?: string | null };

export const api = {
  health: () => request<{ status: string; service: string }>("/health"),
  login: (email: string, password: string) => request<{ authenticated: boolean; user: { email: string; role: string } }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request<{ authenticated: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<{ id: string; email: string; role: string }>("/auth/me"),
  requestMagicLink: (email: string) => request<{ requested: boolean; delivery?: string; token?: string }>("/phase4/magic-link/request", { method: "POST", body: JSON.stringify({ email }) }),
  consumeMagicLink: (token: string) => request<{ authenticated: boolean; user: { id: string; email: string; role: string } }>("/phase4/magic-link/consume", { method: "POST", body: JSON.stringify({ token }) }),
  createInvitation: (email: string, role = "viewer") => request<{ id: string; email: string; role: string; expires_at: string; token: string }>("/phase4/invitations", { method: "POST", body: JSON.stringify({ email, role }) }),
  acceptInvitation: (token: string, password: string) => request<{ authenticated: boolean; user: { id: string; email: string; role: string } }>("/phase4/invitations/accept", { method: "POST", body: JSON.stringify({ token, password }) }),
  getWorkspace: () => request<{ id: string; name: string; slug: string; plan: string; role: string }>("/phase4/workspace"),
  listTags: () => request<Array<{ id: string; name: string; slug: string }>>("/phase4/tags"),
  createTag: (name: string) => request<{ id: string; name: string; slug: string }>("/phase4/tags", { method: "POST", body: JSON.stringify({ name }) }),
  recordUsage: (metric: string, quantity = 1, unit = "unit", idempotency_key?: string) => request("/phase4/usage", { method: "POST", body: JSON.stringify({ metric, quantity, unit, idempotency_key }) }),
  getUsage: () => request<{ period_start: string; totals: Record<string, number> }>("/phase4/usage"),
  getBilling: () => request("/phase4/billing"),
  createCheckout: (plan: "pro" | "business") => request<{ id: string; url: string; plan: string }>("/phase4/billing/checkout?plan=" + encodeURIComponent(plan), { method: "POST" }),
  setPlan: (plan: string) => request("/phase4/billing/plan?plan=" + encodeURIComponent(plan), { method: "POST" }),
  createWebhook: (url: string, events: string[] = []) => request<{ id: string; url: string; events: string[]; secret: string }>("/phase4/webhooks", { method: "POST", body: JSON.stringify({ url, events }) }),
  listWebhooks: () => request<Array<{ id: string; url: string; events: string[]; is_active: boolean }>>("/phase4/webhooks"),
  deleteWebhook: (id: string) => request<{ id: string; is_active: boolean }>(`/phase4/webhooks/${id}`, { method: "DELETE" }),
  createNotification: (event_type: string, payload: Record<string, unknown> = {}) => request<{ id: string; status: string }>("/phase4/notifications", { method: "POST", body: JSON.stringify({ event_type, payload }) }),
  listNotifications: () => request<Array<{ id: string; event_type: string; status: string; attempts: number; created_at: string }>>("/phase4/notifications"),


  listIdeas: () => request<Idea[]>("/ideas"),
  createIdea: (data: { title: string; concept?: string; category?: string; hook?: string; content_warning?: string }) => request<Idea>("/ideas", { method: "POST", body: JSON.stringify(data) }),
  updateIdea: (id: string, data: Partial<Idea>) => request<Idea>(`/ideas/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  listSeries: () => request<Series[]>("/series"),
  createSeries: (data: { title: string; description?: string }) => request<Series>("/series", { method: "POST", body: JSON.stringify(data) }),
  getSeries: (id: string) => request<Series>(`/series/${id}`),
  updateSeries: (id: string, data: Partial<Series>) => request<Series>(`/series/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  listSeasons: (id: string) => request<Season[]>(`/series/${id}/seasons`),
  createSeason: (id: string, data: { season_number: number; title?: string }) => request<Season>(`/series/${id}/seasons`, { method: "POST", body: JSON.stringify(data) }),
  listEpisodes: () => request<Episode[]>("/episodes"),
  createEpisode: (data: { series_id: string; season_id?: string; episode_number: number; title: string; category?: string; synopsis?: string; target_duration_seconds?: number }) => request<Episode>("/episodes", { method: "POST", body: JSON.stringify(data) }),
  getEpisode: (id: string) => request<Episode>(`/episodes/${id}`),
  updateEpisode: (id: string, data: EpisodeUpdateInput) => request<Episode>(`/episodes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  listScripts: (episodeId: string) => request<Script[]>(`/episodes/${episodeId}/scripts`),
  createScript: (episodeId: string, data: { title?: string; content: string }) => request<Script>(`/episodes/${episodeId}/scripts`, { method: "POST", body: JSON.stringify(data) }),
  updateScript: (episodeId: string, scriptId: string, data: { title?: string; content?: string; status?: string; expected_row_version: number }) => request<Script>(`/scripts/${scriptId}`, { method: "PATCH", body: JSON.stringify(data) }),
  createScriptVersion: (episodeId: string, data: { title?: string; content: string }) => request<Script>(`/episodes/${episodeId}/scripts/versions`, { method: "POST", body: JSON.stringify(data) }),
  listScenes: (episodeId: string) => request<Scene[]>(`/episodes/${episodeId}/scenes`),
  createScene: (episodeId: string, data: CreateSceneInput) => request<Scene>(`/episodes/${episodeId}/scenes`, { method: "POST", body: JSON.stringify(data) }),
  updateScene: (episodeId: string, sceneId: string, data: Partial<Scene>) => request<Scene>(`/scenes/${sceneId}`, { method: "PATCH", body: JSON.stringify(data) }),
  reorderScenes: (episodeId: string, sceneIds: string[]) => request<Scene[]>(`/episodes/${episodeId}/scenes/reorder`, { method: "POST", body: JSON.stringify(sceneIds) }),
  listAssets: (episodeId: string) => request<Asset[]>(`/episodes/${episodeId}/assets`),
  updateAsset: (assetId: string, data: Partial<Asset>) => request<Asset>(`/assets/${assetId}`, { method: "PATCH", body: JSON.stringify(data) }),
  listJobs: () => request<ProcessingJob[]>(`/jobs`),
  createMockJob: (episodeId: string) => idempotentRequest<ProcessingJob>(`nf-idempotency:jobs:mock:${episodeId}`, `/jobs/mock`, { method: "POST", body: JSON.stringify({ episode_id: episodeId }) }),
  createRealJob: (episodeId: string) => idempotentRequest<ProcessingJob>(`nf-idempotency:jobs:real:${episodeId}`, `/jobs/real`, { method: "POST", body: JSON.stringify({ episode_id: episodeId }) }),
  retryJob: (jobId: string) => request<ProcessingJob>(`/jobs/${jobId}/retry`, { method: "POST" }),
  listSubtitles: (episodeId: string) => request<Subtitle[]>(`/episodes/${episodeId}/subtitles`),
  generateSubtitle: (episodeId: string, preset = "burmese_default") => request<Subtitle>(`/episodes/${episodeId}/subtitles/generate`, { method: "POST", body: JSON.stringify({ preset }) }),
  updateSubtitle: (subtitleId: string, data: { cues?: SubtitleCue[]; preset?: string; format?: string }) => request<Subtitle>(`/subtitles/${subtitleId}`, { method: "PATCH", body: JSON.stringify(data) }),
  validateSubtitle: (episodeId: string) => request<{ valid: boolean; errors: Subtitle["validation_errors"]; subtitle_id: string }>(`/episodes/${episodeId}/subtitles/validate`, { method: "POST" }),
  approveSubtitle: (episodeId: string) => request<Subtitle>(`/episodes/${episodeId}/subtitles/approve`, { method: "POST" }),
  exportSubtitle: (subtitleId: string, format: "srt" | "vtt") => `${base}/subtitles/${subtitleId}/export?format=${format}`,
  uploadAsset: async (episodeId: string, file: File, assetType: string, sceneId?: string) => {
    if (file.size <= 0) throw new Error("Choose a non-empty file to upload");
    const resumeKey = `nf-upload:${episodeId}:${assetType}:${sceneId ?? ""}:${file.name}:${file.size}:${file.lastModified}`;
    const idempotencyStorageKey = `nf-upload-idempotency:${resumeKey}`;
    const checksumFor = async (chunk: Blob) => Array.from(
      new Uint8Array(await crypto.subtle.digest("SHA-256", await chunk.arrayBuffer())),
    ).map(value => value.toString(16).padStart(2, "0")).join("");
    const readResponse = async <T,>(response: Response): Promise<T> => {
      if (!response.ok) {
        let message = "Upload failed";
        try { const body = await response.json(); message = body.detail ?? message; } catch {}
        throw new UploadResponseError(message, response.status);
      }
      return response.json() as Promise<T>;
    };
    const createSession = async () => {
      const idempotencyKey = localStorage.getItem(idempotencyStorageKey) ?? crypto.randomUUID();
      localStorage.setItem(idempotencyStorageKey, idempotencyKey);
      return readResponse<UploadSession>(await fetch(base + "/uploads", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey,
        },
        body: JSON.stringify({
          episode_id: episodeId,
          original_filename: file.name,
          mime_type: file.type,
          asset_type: assetType,
          expected_size: file.size,
          scene_id: sceneId ?? null,
        }),
      }));
    };

    let session: UploadSession | undefined;
    const savedSessionId = localStorage.getItem(resumeKey);
    if (savedSessionId) {
      const response = await fetch(base + `/uploads/${encodeURIComponent(savedSessionId)}`, {
        credentials: "include",
      });
      if (response.ok) {
        const existing = await response.json() as UploadSession;
        if (
          existing.episode_id === episodeId
          && existing.asset_type === assetType
          && existing.mime_type === file.type
          && existing.expected_size === file.size
          && (existing.scene_id ?? undefined) === sceneId
        ) {
          if (existing.status === "committed" && existing.asset) {
            let committedPartsMatch = existing.parts.length === Math.ceil(file.size / existing.chunk_size);
            for (const part of existing.parts) {
              if (!committedPartsMatch) break;
              const offset = (part.part_number - 1) * existing.chunk_size;
              const chunk = file.slice(offset, Math.min(file.size, offset + existing.chunk_size));
              committedPartsMatch = chunk.size === part.size_bytes
                && await checksumFor(chunk) === part.checksum_sha256;
            }
            if (committedPartsMatch) {
              localStorage.removeItem(resumeKey);
              return existing.asset;
            }
          } else if (existing.status === "active") {
            session = existing;
          }
        }
        if (!session) {
          const deleted = await fetch(base + `/uploads/${encodeURIComponent(savedSessionId)}`, {
            method: "DELETE",
            credentials: "include",
          });
          if (!deleted.ok && ![404, 409, 410].includes(deleted.status)) await readResponse(deleted);
        }
      } else if (response.status !== 404 && response.status !== 410) {
        await readResponse(response);
      }
      if (!session) {
        localStorage.removeItem(resumeKey);
        localStorage.removeItem(idempotencyStorageKey);
      }
    }

    if (!session) {
      session = await createSession();
      localStorage.setItem(resumeKey, session.id);
    }

    const knownParts = new Map(session.parts.map(part => [part.part_number, part]));
    const partCount = Math.ceil(file.size / session.chunk_size);
    for (let partNumber = 1; partNumber <= partCount; partNumber += 1) {
      const offset = (partNumber - 1) * session.chunk_size;
      const chunk = file.slice(offset, Math.min(file.size, offset + session.chunk_size));
      const checksum = await checksumFor(chunk);
      const known = knownParts.get(partNumber);
      if (known && known.size_bytes === chunk.size && known.checksum_sha256 === checksum) continue;

      let lastError: Error | undefined;
      for (let attempt = 0; attempt < 3; attempt += 1) {
        try {
          const response = await fetch(
            base + `/uploads/${encodeURIComponent(session.id)}/chunks?part_number=${partNumber}&offset=${offset}`,
            {
              method: "PUT",
              credentials: "include",
              headers: { "Content-Type": "application/octet-stream" },
              body: chunk,
            },
          );
          if (response.status >= 400 && response.status < 500) await readResponse(response);
          if (!response.ok) await readResponse(response);
          lastError = undefined;
          break;
        } catch (error) {
          if (error instanceof UploadResponseError && error.status < 500) throw error;
          lastError = error instanceof Error ? error : new Error("Chunk upload failed");
          if (attempt < 2) await new Promise(resolve => setTimeout(resolve, 250 * (2 ** attempt)));
        }
      }
      if (lastError) throw lastError;
    }

    const response = await fetch(base + `/uploads/${encodeURIComponent(session.id)}/commit`, {
      method: "POST",
      credentials: "include",
    });
    const asset = await readResponse<Asset>(response);
    localStorage.removeItem(resumeKey);
    localStorage.removeItem(idempotencyStorageKey);
    return asset;
  },
};

export type SubtitleCue = { id?: number; start: number; end: number; text: string };
export type Subtitle = { id: string; episode_id: string; version: number; language: string; format: string; preset: string; cues: SubtitleCue[]; status: string; is_current: boolean; validation_errors: { code: string; cue?: number; message: string }[]; created_at: string; updated_at: string };
