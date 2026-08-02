import type { AxiosResponse } from "axios";

export function unwrapData<T>(response: AxiosResponse<T>) {
  return response.data;
}

export function toArray<T>(value: T[] | undefined | null) {
  return Array.isArray(value) ? value : [];
}
