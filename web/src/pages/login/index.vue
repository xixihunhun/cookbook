<template>
  <view class="page">
    <!-- 红橙渐变背景覆盖 -->
    <view class="bg-gradient"></view>

    <view class="content">
      <!-- 大标题 -->
      <view class="logo">🍳</view>
      <view class="big-title">夫妻点菜</view>
      <view class="sub-title">两个人，一起抽签决定今天吃啥</view>

      <!-- 微信登录大按钮 -->
      <view class="wx-btn" @tap="doWxLogin">
        <view class="wx-logo">💬</view>
        <view class="wx-text">微信一键登录</view>
      </view>

      <!-- H5 / 开发环境：模拟登录 -->
      <view class="mock-area">
        <view class="mock-text">开发调试</view>
        <view class="mock-btn" @tap="doMockLogin">模拟登录（H5）</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import Taro from "@tarojs/taro";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();

async function doWxLogin() {
  try {
    await userStore.login();
    Taro.showToast({ title: "登录成功", icon: "success" });
    // 登录成功 → 看情况跳家庭绑定或投票
    const target = userStore.familyId
      ? "/pages/vote/vote"
      : "/pages/family/bind";
    setTimeout(() => {
      Taro.switchTab({ url: target }).catch(() => {
        Taro.redirectTo({ url: "/pages/index/index" });
      });
    }, 500);
  } catch (e: any) {
    // 如果 Taro.login 在 H5 报错，自动降级到模拟
    Taro.showToast({ title: e?.message || "登录失败", icon: "none" });
  }
}

async function doMockLogin() {
  try {
    const nickname = "测试小伙伴" + Math.floor(Math.random() * 100);
    await userStore.loginMock(nickname);
    Taro.showToast({ title: "模拟登录成功", icon: "success" });
    setTimeout(() => {
      const target = userStore.familyId
        ? "/pages/vote/vote"
        : "/pages/family/bind";
      Taro.switchTab({ url: target }).catch(() => {
        Taro.redirectTo({ url: "/pages/index/index" });
      });
    }, 500);
  } catch (e: any) {
    Taro.showToast({ title: e?.message || "失败", icon: "none" });
  }
}
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page { height: 100vh; position: relative; overflow: hidden; }
.bg-gradient {
  position: absolute;
  inset: 0;
  background: $bg-gradient;
  z-index: 0;
}
.content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 60px;
}

/* Logo + 标题 */
.logo {
  font-size: 160px;
  margin-bottom: 20px;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.2));
}
.big-title {
  font-size: 72px;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  letter-spacing: 4px;
}
.sub-title {
  font-size: 28px;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 12px;
  margin-bottom: 80px;
}

/* 微信登录按钮（绿色 + 微信 logo） */
.wx-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  width: 100%;
  padding: 32px;
  background: #07C160;
  border-radius: 60px;
  box-shadow: 0 8px 24px rgba(7, 193, 96, 0.4);

  &:active { opacity: 0.9; }
}
.wx-logo {
  font-size: 56px;
  line-height: 1;
}
.wx-text {
  font-size: 34px;
  font-weight: 700;
  color: #fff;
}

/* 模拟登录区域 */
.mock-area { margin-top: 40px; text-align: center; }
.mock-text { font-size: 24px; color: rgba(255, 255, 255, 0.7); margin-bottom: 12px; }
.mock-btn {
  padding: 16px 40px;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 40px;
  font-size: 26px;
  font-weight: 600;

  &:active { opacity: 0.8; }
}
</style>
