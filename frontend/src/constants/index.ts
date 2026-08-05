export const APP_NAME = "Let Him Cook !!";
const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "https://lethimcook-backend-jekx.onrender.com/api";
export const API_BASE_URL = rawApiUrl.replace(/\/+$/, "");

export const AUTH_STORAGE_KEY = "let-him-cook-auth";
export const QUERY_STALE_TIME_MS = 30_000;
