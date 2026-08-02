import { apiClient } from "@/lib/axios";
import type { RecipeData, RecipeIngredient } from "@/types/api";

export async function getRecipe(dishName: string): Promise<RecipeData> {
  const response = await apiClient.get(`/recipes/${encodeURIComponent(dishName)}`);
  const rawData = response.data as any;
  if (!rawData) {
    return { dishName };
  }

  const recipeObj = rawData.recipe_json || rawData;
  const ingredientsObj = rawData.ingredients_json || recipeObj.ingredients || [];

  let ingredients: RecipeIngredient[] = [];

  if (Array.isArray(ingredientsObj)) {
    ingredients = ingredientsObj;
  } else if (ingredientsObj && typeof ingredientsObj === "object") {
    if (Array.isArray(ingredientsObj.items)) {
      ingredients = ingredientsObj.items;
    } else if (Array.isArray(ingredientsObj.ingredients)) {
      ingredients = ingredientsObj.ingredients;
    } else {
      ingredients = Object.entries(ingredientsObj).map(([name, qty]) => {
        if (typeof qty === "object" && qty !== null) {
          return {
            name: (qty as any).name || name,
            qty: String((qty as any).qty || (qty as any).quantity || "1 item"),
            price: (qty as any).price,
            icon: (qty as any).icon || (qty as any).emoji,
          };
        }
        return { name, qty: String(qty) };
      });
    }
  }

  // Ensure every ingredient item has a valid string name
  const normalizedIngredients: RecipeIngredient[] = ingredients.map((ing: any) => {
    if (typeof ing === "string") return { name: ing, qty: "1 item" };
    const name = typeof ing.name === "string" ? ing.name : typeof ing.ingredient === "string" ? ing.ingredient : "Ingredient";
    return {
      name,
      qty: String(ing.qty ?? ing.quantity ?? "1 item"),
      price: ing.price,
      emoji: ing.emoji ?? ing.icon,
      icon: ing.icon ?? ing.emoji,
    };
  });

  const steps = Array.isArray(recipeObj.steps)
    ? recipeObj.steps
    : Array.isArray(recipeObj.instructions)
      ? recipeObj.instructions
      : Array.isArray(recipeObj.recipe_steps)
        ? recipeObj.recipe_steps
        : [];

  return {
    dishName: rawData.dish_name ?? rawData.dishName ?? dishName,
    title: rawData.dish_name ?? rawData.dishName ?? dishName,
    steps,
    ingredients: normalizedIngredients,
    timeMinutes: rawData.estimated_cooking_time ?? recipeObj.estimated_cooking_time ?? recipeObj.timeMinutes,
    difficulty: recipeObj.difficulty ?? "Medium",
    cost: recipeObj.cost != null ? Number(recipeObj.cost) : undefined,
  };
}