import { apiClient } from "@/lib/axios";
import type { OrderInput, OrderRecord } from "@/types/api";

export async function createOrder(payload: OrderInput): Promise<OrderRecord> {
  const reqBody = {
    dish_name: payload.dish_name || payload.dishName,
  };
  const response = await apiClient.post("/orders", reqBody);
  const resData = response.data as { order_id?: number; id?: number; status?: string; message?: string };
  return {
    id: resData.order_id ?? resData.id,
    dish_name: payload.dish_name || payload.dishName,
    dishName: payload.dish_name || payload.dishName,
    status: resData.status ?? "pending",
  };
}

export async function getOrders(): Promise<OrderRecord[]> {
  const response = await apiClient.get("/orders");
  const rawData = response.data;
  if (Array.isArray(rawData)) {
    return rawData.map((item: any) => ({
      id: item.id,
      dishName: item.dish_name ?? item.dishName,
      dish_name: item.dish_name ?? item.dishName,
      status: item.status,
      total: item.total_cost != null ? Number(item.total_cost) : item.total,
      cost: item.total_cost != null ? Number(item.total_cost) : item.cost,
      createdAt: item.created_at,
    }));
  }
  const data = rawData as { data?: OrderRecord[]; items?: OrderRecord[]; results?: OrderRecord[] };
  return data.data ?? data.items ?? data.results ?? [];
}

export async function getOrderById(orderId: string | number): Promise<OrderRecord> {
  const response = await apiClient.get(`/orders/${orderId}`);
  return response.data as OrderRecord;
}