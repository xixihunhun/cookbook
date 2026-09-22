<template>
  <view class="page">
    <!-- 未登录 → 引导 -->
    <block v-if="!isLoggedIn">
      <view class="card guide-card">
        <view class="guide-icon">🔐</view>
        <view class="guide-title">你还没登录</view>
        <view class="guide-sub">登录后查看你的家庭、收藏等</view>
        <view class="btn btn-primary btn-block" @tap="goLogin">立即登录</view>
      </view>
    </block>

    <!-- 已登录 -->
    <block v-else>
      <!-- 顶部渐变 + 头像 -->
      <view class="profile-hero">
        <image class="avatar" :src="user?.avatar || defaultAvatar" mode="aspectFill" />
        <view class="profile-info">
          <view class="nickname">{{ user?.nickname || user?.username || '小伙伴' }}</view>
          <view class="family-tag" @tap="goFamily">
            <text v-if="familyName">🏠 {{ familyName }} ›</text>
            <text v-else>🏠 去绑定家庭 ›</text>
          </view>
        </view>
      </view>

      <!-- 菜单列表 -->
      <view class="card menu-card">
        <view class="menu-item" @tap="goMyRecipes">
          <text class="menu-icon">📖</text>
          <text class="menu-label">我的发布</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @tap="goMyFavorites">
          <text class="menu-icon">⭐</text>
          <text class="menu-label">我的收藏</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @tap="goFamilyMine">
          <text class="menu-icon">🏡</text>
          <text class="menu-label">我的家庭</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @tap="goVote">
          <text class="menu-icon">🎲</text>
          <text class="menu-label">去投票</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 红色退出登录 -->
      <view class="btn btn-danger btn-block logout" @tap="doLogout">退出登录</view>
    </block>
  </view>
</template>

<script setup lang="ts">
import Taro from "@tarojs/taro";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const { isLoggedIn, user, familyName } = userStore;

const defaultAvatar = "https://img.icons8.com/color/96/user-male-circle--v1.png";

function goLogin() { Taro.navigateTo({ url: "/pages/login/index" }); }
function goFamily() {
  Taro.navigateTo({
    url: familyName.value ? "/pages/family/mine" : "/pages/family/bind",
  });
}
function goFamilyMine() { Taro.navigateTo({ url: "/pages/family/mine" }); }
function goMyRecipes() {
  Taro.showToast({ title: "功能开发中", icon: "none" });
}
function goMyFavorites() {
  Taro.showToast({ title: "功能开发中", icon: "none" });
}
function goVote() { Taro.switchTab({ url: "/pages/vote/vote" }); }

function doLogout() {
  Taro.showModal({
    title: "确认退出",
    content: "确定要退出登录吗？",
    success: (r) => {
      if (!r.confirm) return;
      userStore.logout();
      Taro.showToast({ title: "已退出", icon: "none" });
      Taro.switchTab({ url: "/pages/index/index" });
    },
  });
}
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page { padding-bottom: 60px; }

/* ===== 引导卡 ===== */
.guide-card { text-align: center; padding: 80px 40px; }
.guide-icon { font-size: 140px; margin-bottom: 20px; }
.guide-title { font-size: 36px; font-weight: 700; color: #222; }
.guide-sub { font-size: 26px; color: #999; margin: 12px 0 32px; }

/* ===== 顶部个人信息 ===== */
.profile-hero {
  background: $bg-gradient;
  padding: 60px 40px 50px;
  display: flex;
  align-items: center;
  gap: 28px;
  border-bottom-left-radius: 32px;
  border-bottom-right-radius: 32px;
  box-shadow: 0 8px 32px rgba(255, 45, 45, 0.2);
}
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.5);
  background: #fff;
}
.profile-info { flex: 1; }
.nickname {
  font-size: 40px;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
.family-tag {
  display: inline-block;
  margin-top: 8px;
  padding: 6px 20px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  font-size: 24px;
  color: #fff;

  &:active { opacity: 0.85; }
}

/* ===== 菜单 ===== */
.menu-card { padding: 8px 28px; margin-top: 24px; }
.menu-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 28px 0;
  border-bottom: 1px solid #FFE0D6;

  &:last-child { border-bottom: none; }
  &:active { background: #FFF9F5; }
}
.menu-icon { font-size: 40px; width: 56px; text-align: center; }
.menu-label { flex: 1; font-size: 30px; color: #333; }
.menu-arrow { font-size: 36px; color: #ccc; }

.logout { margin: 24px; }
</style>
