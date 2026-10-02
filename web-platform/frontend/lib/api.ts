const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(base + path, { ...init, headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) } });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export const api = {
  health: () => request<{ status: string; service: string }>("/health"),
  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: (token: string) => request<{ id: string; email: string; role: string }>("/auth/me", { headers: { Authorization: "Bearer " + token } }),
};