export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }

  let token = localStorage.getItem("access_token") || localStorage.getItem("token");
  if (!token && process.env.NODE_ENV !== "production") {
    token = "mock_token_for_development";
    localStorage.setItem("access_token", token);
  }

  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function buildHeaders(overrides?: Record<string, string>): Record<string, string> {
  return { ...getAuthHeaders(), ...(overrides || {}) };
}
