import { http } from "./request";
import type { WxLoginResult, User } from "@/types";

/** 微信小程序登录：把 wx.login 的 code 传给后端换 token */
export function wxLogin(data: { code: string; nickname?: string; avatar?: string }) {
  return http.post<WxLoginResult>("/api/user/wx-login", data);
}

/** 后端开发环境模拟登录（H5 调试用） */
export function mockLogin(nickname = "测试用户", avatar = "") {
  return http.post<WxLoginResult>("/api/user/wx-login", {
    code: "mock_" + Date.now(),
    nickname,
    avatar,
  });
}

export function getProfile() {
  return http.get<User>("/api/user/profile");
}

export function updateProfile(data: Partial<User>) {
  return http.put<User>("/api/user/profile", data);
}
