import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL } from "@/constants";
import { useAuthStore } from "@/store";
import type { AuthSession, ApiErrorPayload } from "@/types/api";

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshPromise: Promise<string | null> | null = null;

function readTokenValue(payload: AuthSession | Record<string, unknown> | null | undefined) {
  if (!payload || typeof payload !== "object") {
    return { accessToken: null, refreshToken: null, user: null };
  }

  const normalized = payload as Record<string, unknown>;
  const accessToken =
    (normalized.accessToken as string | undefined) ??
    (normalized.access_token as string | undefined) ??
    (normalized.token as string | undefined) ??
    null;
  const refreshToken =
    (normalized.refreshToken as string | undefined) ??
    (normalized.refresh_token as string | undefined) ??
    null;
  const user = (normalized.user as AuthSession["user"]) ?? null;

  return { accessToken, refreshToken, user };
}

async function refreshAccessToken() {
  const { refreshToken } = useAuthStore.getState();
  if (!refreshToken) {
    return null;
  }

  const response = await refreshClient.post("/auth/refresh", {
    refreshToken,
    refresh_token: refreshToken,
  });

  const { accessToken, refreshToken: nextRefreshToken, user } = readTokenValue(response.data as AuthSession);
  if (!accessToken) {
    return null;
  }

  useAuthStore.getState().setSession({
    accessToken,
    refreshToken: nextRefreshToken ?? refreshToken,
    user,
  });

  return accessToken;
}

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorPayload>) => {
    const status = error.response?.status;
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (status !== 401 || !originalRequest || originalRequest._retry || originalRequest.url?.includes("/auth/refresh")) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const nextAccessToken = await refreshPromise;
      if (!nextAccessToken) {
        useAuthStore.getState().clearSession();
        return Promise.reject(error);
      }

      originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      useAuthStore.getState().clearSession();
      return Promise.reject(refreshError);
    }
  }
);
