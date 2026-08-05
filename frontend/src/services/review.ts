import { apiClient } from "@/lib/axios";
import type { ReviewData } from "@/types/api";

export async function getReviews(): Promise<ReviewData[]> {
  const response = await apiClient.get("/reviews");
  const rawData = response.data;
  if (Array.isArray(rawData)) {
    return rawData.map((item: any) => ({
      score: item.score != null ? Number(item.score) : 9.8,
      rating: item.score != null ? Number(item.score) : 9.8,
      reward: item.bonus_coins != null ? Number(item.bonus_coins) : 0,
      categories: [
        { name: "Taste & Flavor", score: item.score != null ? Number(item.score) : 9.8, comment: item.review ?? "Delicious!", icon: "👅" },
      ],
    }));
  }
  const data = rawData as { data?: ReviewData[]; items?: ReviewData[]; results?: ReviewData[] };
  return data.data ?? data.items ?? data.results ?? [];
}

export async function getReviewByDish(dishName: string): Promise<ReviewData> {
  try {
    const response = await apiClient.get(`/reviews/${encodeURIComponent(dishName)}`);
    const suggestions = Array.isArray(response.data) ? response.data : [];
    return {
      dishName,
      dish_name: dishName,
      score: response.data?.score != null ? Number(response.data.score) : 0,
      rating: response.data?.score != null ? Number(response.data.score) : 0,
      reward: response.data?.bonus_coins != null ? Number(response.data.bonus_coins) : 0,
      categories: [
        { name: "Taste & Flavor", score: response.data?.score != null ? Number(response.data.score) : 0, comment: suggestions[0] || response.data?.review || "Waiting for food...", icon: "👅" },
        { name: "Aroma & Heat", score: response.data?.score != null ? Number(response.data.score) : 0, comment: suggestions[1] || "Waiting for food...", icon: "👃" },
        { name: "Presentation", score: response.data?.score != null ? Number(response.data.score) : 0, comment: suggestions[2] || "Waiting for food...", icon: "🎨" },
      ],
    };
  } catch {
    return {
      dishName,
      score: 0,
      rating: 0,
      reward: 0,
      categories: [
        { name: "Taste & Flavor", score: 0, comment: "Waiting for food...", icon: "👅" },
        { name: "Aroma", score: 0, comment: "Waiting for food...", icon: "👃" },
        { name: "Presentation", score: 0, comment: "Waiting for food...", icon: "🎨" },
      ],
    };
  }
}

