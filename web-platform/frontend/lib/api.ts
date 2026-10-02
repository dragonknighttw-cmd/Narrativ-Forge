const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(base + path, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    let message = "Request failed";
    try { const body = await response.json(); message = body.detail ?? message; } catch {}
    throw new Error(message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export type Idea = { id: string; title: string; concept?: string | null; category?: string | null; hook?: string | null; content_warning?: string | null; status: string; created_at: string };
export type Series = { id: string; title: string; description?: string | null; status: string; created_at: string };
export type Season = { id: string; series_id: string; season_number: number; title?: string | null; created_at: string };
export type Episode = { id: string; public_id: string; series_id: string; season_id?: string | null; episode_number: number; title: string; category?: string | null; synopsis?: string | null; target_duration_seconds: number; actual_duration_seconds?: number | null; status: string; current_step: string; created_at: string; updated_at: string };
export type Script = { id: string; episode_id: string; version: number; title?: string | null; content: string; status: string; is_current: boolean; created_at: string; updated_at: string };
export type Scene = { id: string; episode_id: string; script_id?: string | null; scene_number: number; purpose: string; description?: string | null; dialogue?: string | null; duration_seconds?: number | null; created_at: string; updated_at: string };
export type Asset = { id: string; episode_id: string; scene_id?: string | null; asset_type: string; original_filename: string; storage_provider: string; local_path?: string | null; mime_type: string; file_size_bytes: number; version: number; copyright_status: string; is_final: boolean; status: string; created_at: string };
export type CreateSceneInput = { scene_number: number; script_id?: string; purpose: string; description?: string; dialogue?: string; duration_seconds?: number };
export type ProcessingJob = { id: string; episode_id: string; job_type: string; status: string; progress: number; retry_count: number; input_asset_id?: string | null; output_asset_id?: string | null; error_code?: string | null; error_message?: string | null; created_at: string; completed_at?: string | null };

export const api = {
  health: () => request<{ status: string; service: string }>("/health"),
  login: (email: string, password: string) => request<{ authenticated: boolean; user: { email: string; role: string } }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request<{ authenticated: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<{ id: string; email: string; role: string }>("/auth/me"),
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
  updateEpisode: (id: string, data: Partial<Episode>) => request<Episode>(`/episodes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  listScripts: (episodeId: string) => request<Script[]>(`/episodes/${episodeId}/scripts`),
  createScript: (episodeId: string, data: { title?: string; content: string }) => request<Script>(`/episodes/${episodeId}/scripts`, { method: "POST", body: JSON.stringify(data) }),
  updateScript: (episodeId: string, scriptId: string, data: Partial<Script>) => request<Script>(`/scripts/${scriptId}`, { method: "PATCH", body: JSON.stringify(data) }),
  createScriptVersion: (episodeId: string, data: { title?: string; content: string }) => request<Script>(`/episodes/${episodeId}/scripts/versions`, { method: "POST", body: JSON.stringify(data) }),
  listScenes: (episodeId: string) => request<Scene[]>(`/episodes/${episodeId}/scenes`),
  createScene: (episodeId: string, data: CreateSceneInput) => request<Scene>(`/episodes/${episodeId}/scenes`, { method: "POST", body: JSON.stringify(data) }),
  updateScene: (episodeId: string, sceneId: string, data: Partial<Scene>) => request<Scene>(`/scenes/${sceneId}`, { method: "PATCH", body: JSON.stringify(data) }),
  reorderScenes: (episodeId: string, sceneIds: string[]) => request<Scene[]>(`/episodes/${episodeId}/scenes/reorder`, { method: "POST", body: JSON.stringify(sceneIds) }),
  listAssets: (episodeId: string) => request<Asset[]>(`/episodes/${episodeId}/assets`),
  updateAsset: (assetId: string, data: Partial<Asset>) => request<Asset>(`/assets/${assetId}`, { method: "PATCH", body: JSON.stringify(data) }),
  listJobs: () => request<ProcessingJob[]>(`/jobs`),
  createMockJob: (episodeId: string) => request<ProcessingJob>(`/jobs/mock`, { method: "POST", body: JSON.stringify({ episode_id: episodeId }) }),
  createRealJob: (episodeId: string) => request<ProcessingJob>(`/jobs/real`, { method: "POST", body: JSON.stringify({ episode_id: episodeId }) }),
  retryJob: (jobId: string) => request<ProcessingJob>(`/jobs/${jobId}/retry`, { method: "POST" }),
  listSubtitles: (episodeId: string) => request<Subtitle[]>(`/episodes/${episodeId}/subtitles`),
  generateSubtitle: (episodeId: string, preset = "burmese_default") => request<Subtitle>(`/episodes/${episodeId}/subtitles/generate`, { method: "POST", body: JSON.stringify({ preset }) }),
  updateSubtitle: (subtitleId: string, data: { cues?: SubtitleCue[]; preset?: string; format?: string }) => request<Subtitle>(`/subtitles/${subtitleId}`, { method: "PATCH", body: JSON.stringify(data) }),
  validateSubtitle: (episodeId: string) => request<{ valid: boolean; errors: Subtitle["validation_errors"]; subtitle_id: string }>(`/episodes/${episodeId}/subtitles/validate`, { method: "POST" }),
  approveSubtitle: (episodeId: string) => request<Subtitle>(`/episodes/${episodeId}/subtitles/approve`, { method: "POST" }),
  exportSubtitle: (subtitleId: string, format: "srt" | "vtt") => `${base}/subtitles/${subtitleId}/export?format=${format}`,
  uploadAsset: async (episodeId: string, file: File, assetType: string, sceneId?: string) => {
    const form = new FormData();
    form.append("file", file); form.append("asset_type", assetType);
    if (sceneId) form.append("scene_id", sceneId);
    const response = await fetch(base + `/episodes/${episodeId}/assets/upload`, { method: "POST", credentials: "include", body: form });
    if (!response.ok) { let message = "Upload failed"; try { const body = await response.json(); message = body.detail ?? message; } catch {} throw new Error(message); }
    return response.json() as Promise<Asset>;
  },
};

export type SubtitleCue = { id?: number; start: number; end: number; text: string };
export type Subtitle = { id: string; episode_id: string; version: number; language: string; format: string; preset: string; cues: SubtitleCue[]; status: string; is_current: boolean; validation_errors: { code: string; cue?: number; message: string }[]; created_at: string; updated_at: string };
