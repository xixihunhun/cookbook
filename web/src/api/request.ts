import Taro from "@tarojs/taro";
import type { ApiResponse } from "@/types";

/**
 * Taro 跨端请求封装
 * - H5: 用 proxy（config 里 devServer proxy 到 Flask）
 * - 小程序: 用电脑局域网 IP（微信开发者工具需勾选"不校验合法域名"）
 * - RN: 同小程序
 */
const LAN_IP = "192.168.1.145"; // ← 改成你电脑的局域网 IP

const BASE_URL = (() => {
  const env = process.env.TARO_ENV;
  if (env === "h5") return "";          // H5 走 devServer proxy
  if (env === "weapp") return `http://${LAN_IP}:5000`; // 小程序用局域网 IP
  return `http://${LAN_IP}:5000`;       // RN 也用 IP
})();

function getToken(): string {
  return Taro.getStorageSync("token") || "";
}

function setToken(t: string) {
  Taro.setStorageSync("token", t);
}

function clearToken() {
  Taro.removeStorageSync("token");
  Taro.removeStorageSync("user");
}

function showToast(msg: string, icon: "success" | "none" = "none") {
  Taro.showToast({ title: msg, icon, duration: 1500 });
}

export function request<T>(
  path: string,
  method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
  data?: unknown
): Promise<ApiResponse<T>> {
  const url = BASE_URL + path;
  const header: Record<string, string> = { "content-type": "application/json" };
  const token = getToken();
  if (token) header["Authorization"] = `Bearer ${token}`;

  return new Promise((resolve, reject) => {
    Taro.request({
      url,
      method,
      data,
      header,
      success: (res) => {
        const body = res.data as ApiResponse<T>;
        if (body.code === 401) {
          clearToken();
          showToast(body.msg || "登录已过期");
          const pages = Taro.getCurrentPages();
          const cur = pages[pages.length - 1];
          if (cur && cur.route !== "pages/login/index") {
            Taro.navigateTo({ url: "/pages/login/index" });
          }
          reject(new Error(body.msg));
          return;
        }
        if (body.code !== 200) {
          showToast(body.msg || "请求失败");
          reject(new Error(body.msg));
          return;
        }
        resolve(body);
      },
      fail: (err) => {
        showToast("网络错误，请稍后重试");
        reject(err);
      },
    });
  });
}

export const http = {
  get: <T>(path: string, params?: Record<string, unknown>) =>
    request<T>(path + (params ? "?" + new URLSearchParams(params as any).toString() : ""), "GET"),
  post: <T>(path: string, data?: unknown) => request<T>(path, "POST", data),
  put: <T>(path: string, data?: unknown) => request<T>(path, "PUT", data),
  del: <T>(path: string) => request<T>(path, "DELETE"),
};

export const storage = { getToken, setToken, clearToken };
