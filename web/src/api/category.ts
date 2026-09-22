import { http } from "./request";
import type { Category } from "@/types";

export function listCategories() {
  return http.get<Category[]>("/api/category/list");
}
