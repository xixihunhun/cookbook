import { http } from "./request";
import type { Family } from "@/types";

/** 获取我所在的家庭 */
export function getMyFamily() {
  return http.get<Family | null>("/api/family/mine");
}

/** 创建家庭 */
export function createFamily(name: string) {
  return http.post<Family>("/api/family/create", { name });
}

/** 通过邀请码加入家庭 */
export function joinFamily(invite_code: string) {
  return http.post<Family>("/api/family/join", { invite_code });
}

/** 退出家庭 */
export function leaveFamily() {
  return http.post<null>("/api/family/leave");
}
