import { http } from "./request";
import type { Recipe, VoteTodayResult, VoteHistoryItem } from "@/types";

/** 推荐菜谱池（今日投票候选池） */
export function recommend() {
  return http.get<Recipe[]>("/api/vote/recommend");
}

/** 投票 / 改投 */
export function castVote(recipe_id: number) {
  return http.post<VoteTodayResult>("/api/vote/cast", { recipe_id });
}

/** 今日投票结果 */
export function todayResult() {
  return http.get<VoteTodayResult>("/api/vote/today");
}

/** 历史投票记录 */
export function history(days = 7) {
  return http.get<VoteHistoryItem[]>("/api/vote/history", { days: days as any });
}
