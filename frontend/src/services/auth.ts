import { apiClient } from "@/lib/axios";
import type { AuthSession, AuthUser } from "@/types/api";

export interface LoginPayload {
  identifier?: string;
  email?: string;
  username?: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  name?: string;
}

function normalizeSession(payload: unknown, user: AuthUser | null = null): AuthSession {
  if (!payload || typeof payload !== "object") {
    return { user };
  }

  const data = payload as Record<string, unknown>;
  return {
    accessToken: (data.accessToken as string | undefined) ?? (data.access_token as string | undefined) ?? (data.token as string | undefined),
    refreshToken: (data.refreshToken as string | undefined) ?? (data.refresh_token as string | undefined),
    tokenType: (data.tokenType as string | undefined) ?? (data.token_type as string | undefined),
    expiresAt: (data.expiresAt as string | number | undefined) ?? (data.expires_at as string | number | undefined),
    user: (data.user as AuthUser | undefined) ?? user,
  };
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await apiClient.get("/auth/me");
  const data = response.data as { id: number; username: string; email: string; wallet_balance?: number };
  return {
    id: data.id,
    username: data.username,
    email: data.email,
    displayName: data.username,
    name: data.username,
  };
}

export async function register(payload: RegisterPayload): Promise<AuthSession> {
  const regBody = {
    username: payload.username || (payload.email ? payload.email.split("@")[0] : "user"),
    email: payload.email,
    password: payload.password,
  };
  await apiClient.post("/auth/register", regBody);
  // Auto-login after registration
  return login({ identifier: regBody.username, password: regBody.password });
}

export async function login(payload: LoginPayload): Promise<AuthSession> {
  const loginBody = {
    identifier: payload.identifier || payload.username || payload.email || "",
    password: payload.password,
  };
  const response = await apiClient.post("/auth/login", loginBody);
  const session = normalizeSession(response.data);

  if (session.accessToken) {
    try {
      const user = await apiClient.get("/auth/me", {
        headers: { Authorization: `Bearer ${session.accessToken}` },
      });
      const userData = user.data as { id: number; username: string; email: string; wallet_balance?: number };
      session.user = {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        displayName: userData.username,
        name: userData.username,
      };
    } catch {
      // Ignore user detail fetch error fallback
    }
  }

  return session;
}

export async function refreshToken(): Promise<AuthSession> {
  const response = await apiClient.post("/auth/refresh");
  return normalizeSession(response.data);
}

export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout");
}

