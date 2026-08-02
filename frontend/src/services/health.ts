import { apiClient } from "@/lib/axios";

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get("/health");
    return response.data?.status === "healthy" || response.status === 200;
  } catch {
    return false;
  }
}
