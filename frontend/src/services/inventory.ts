import { apiClient } from "@/lib/axios";
import type { InventoryData } from "@/types/api";

export async function getInventory(): Promise<InventoryData> {
  const response = await apiClient.get("/inventory");
  const rawData = response.data;
  if (Array.isArray(rawData)) {
    const mappedItems = rawData.map((item: any) => ({
      id: item.id,
      name: item.ingredient_name ?? item.name,
      quantity: item.quantity,
      unit: item.unit,
      price: item.purchase_price ?? item.price,
      emoji: item.emoji ?? "🥗",
      status: "Fresh",
    }));
    return { items: mappedItems };
  }
  return rawData as InventoryData;
}

