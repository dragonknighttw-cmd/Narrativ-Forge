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

export type Idea = { id: string; title: string; concept?: string | null; category?: string | null; hook?: string | null; status: string; created_at: string };
export type Series = { id: string; title: string; description?: string | null; status: string; created_at: string };
export type Season = { id: string; series_id: string; season_number: number; title?: string | null; created_at: string };
export type Episode = { id: string; public_id: string; series_id: string; season_id?: string | null; episode_number: number; title: string; category?: string | null; synopsis?: string | null; target_duration_seconds: number; actual_duration_seconds?: number | null; status: string; current_step: string; created_at: string; updated_at: string };

export const api = {
  health: () => request<{ status: string; service: string }>("/health"),
  login: (email: string, password: string) => request<{ authenticated: boolean; user: { email: string; role: string } }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: () => request<{ authenticated: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<{ id: string; email: string; role: string }>("/auth/me"),
  listIdeas: () => request<Idea[]>("/ideas"),
  createIdea: (data: { title: string; concept?: string; category?: string; hook?: string }) => request<Idea>("/ideas", { method: "POST", body: JSON.stringify(data) }),
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
};
