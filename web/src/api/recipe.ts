import { http } from "./request";
import type { ApiResponse, Recipe, Paginated } from "@/types";

export function listRecipes(params: { page?: number; per_page?: number; category_id?: number; keyword?: string }) {
  return http.get<Paginated<Recipe>>("/api/recipe/list", params as any);
}

export function getRecipe(id: number) {
  return http.get<Recipe>(`/api/recipe/${id}`);
}

export function randomRecipe(count = 1) {
  return http.get<Recipe | Recipe[]>(`/api/recipe/random?count=${count}`);
}

export function addRecipe(data: Partial<Recipe>) {
  return http.post<Recipe>("/api/recipe/add", data);
}

export function editRecipe(id: number, data: Partial<Recipe>) {
  return http.put<Recipe>(`/api/recipe/edit/${id}`, data);
}

export function deleteRecipe(id: number) {
  return http.del<null>(`/api/recipe/delete/${id}`);
}

export function toggleCollect(id: number) {
  return http.post<{ is_collect: boolean }>(`/api/recipe/collect/${id}`);
}

export function listFavorites(params: { page?: number; per_page?: number }) {
  return http.get<Paginated<Recipe>>("/api/recipe/collect/list", params as any);
}

export function listMine(params: { page?: number; per_page?: number }) {
  return http.get<Paginated<Recipe>>("/api/recipe/mine", params as any);
}
