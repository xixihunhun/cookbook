import { defineStore } from "pinia";
import { ref, computed } from "vue";
import Taro from "@tarojs/taro";
import { wxLogin as wxLoginApi, mockLogin } from "@/api/user";
import { getMyFamily } from "@/api/family";
import type { User, Family } from "@/types";

export const useUserStore = defineStore("user", () => {
  // ===== 状态 =====
  const token = ref<string>(Taro.getStorageSync("token") || "");
  const user = ref<User | null>(Taro.getStorageSync("user") || null);
  const family = ref<Family | null>(Taro.getStorageSync("family") || null);

  const isLoggedIn = computed(() => !!token.value);
  const familyId = computed(() => family.value?.id ?? null);
  const familyName = computed(() => family.value?.name ?? "");

  // ===== 登录（微信 / 模拟） =====
  /**
   * 微信登录主流程：
   * - 小程序: Taro.login() 拿 code → 调后端 wx-login
   * - H5/RN: 没有 wx 对象时走 mock
   */
  async function login() {
    let code = "";
    let nickname = "";
    let avatar = "";

    // 1. 尝试 Taro.login（微信环境）
    try {
      const res = await Taro.login();
      code = res.code || "";
    } catch (e) {
      // H5 下 Taro.login 可能失败，忽略
    }

    // 2. 尝试拿昵称/头像（新接口）
    try {
      const profile = await Taro.getUserProfile({ desc: "用于完善用户资料" });
      nickname = profile.userInfo?.nickName || "";
      avatar = profile.userInfo?.avatarUrl || "";
    } catch (e) {
      // 用户拒绝或 H5 环境，忽略
    }

    // 3. 调后端
    const loginReq = code
      ? () => wxLoginApi({ code, nickname, avatar })
      : () => mockLogin(nickname || "小伙伴", avatar);

    const res = await loginReq();
    token.value = res.data.token;
    user.value = res.data.user;
    Taro.setStorageSync("token", res.data.token);
    Taro.setStorageSync("user", res.data.user);

    // 4. 顺手拉一下家庭信息
    try { await refreshFamily(); } catch {}

    return res.data;
  }

  /** 纯模拟登录（H5 开发调试按钮用） */
  async function loginMock(nickname = "测试小伙伴") {
    const res = await mockLogin(nickname);
    token.value = res.data.token;
    user.value = res.data.user;
    Taro.setStorageSync("token", res.data.token);
    Taro.setStorageSync("user", res.data.user);
    try { await refreshFamily(); } catch {}
    return res.data;
  }

  // ===== 家庭 =====
  async function refreshFamily() {
    if (!token.value) { family.value = null; return null; }
    try {
      const res = await getMyFamily();
      family.value = res.data || null;
      Taro.setStorageSync("family", family.value);
      return family.value;
    } catch (e) {
      family.value = null;
      Taro.removeStorageSync("family");
      return null;
    }
  }

  function setFamily(f: Family | null) {
    family.value = f;
    if (f) Taro.setStorageSync("family", f);
    else Taro.removeStorageSync("family");
  }

  // ===== 登出 =====
  function logout() {
    token.value = "";
    user.value = null;
    family.value = null;
    Taro.removeStorageSync("token");
    Taro.removeStorageSync("user");
    Taro.removeStorageSync("family");
  }

  return {
    // state
    token, user, family,
    // computed
    isLoggedIn, familyId, familyName,
    // actions
    login, loginMock, refreshFamily, setFamily, logout,
  };
});
