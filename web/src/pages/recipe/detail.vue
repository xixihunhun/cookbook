<template>
  <view class="page" v-if="recipe">
    <!-- 大封面图 -->
    <image class="cover" :src="recipe.cover_img || defaultCover" mode="aspectFill" />
    <view class="cover-shade"></view>

    <!-- 标题区（覆盖在封面下沿） -->
    <view class="title-box">
      <view class="recipe-title">{{ recipe.title }}</view>
      <view class="recipe-meta">
        <text class="badge-tag">{{ recipe.category_name || '家常菜' }}</text>
        <text class="meta-item">⏱ {{ recipe.cook_time || '未知' }}</text>
        <text class="meta-item">👁 {{ recipe.views }} 浏览</text>
      </view>
    </view>

    <!-- 食材列表 -->
    <view class="section">
      <view class="section-title">🥬 食材</view>
      <view class="material-box">
        <view
          v-for="(m, i) in materials"
          :key="i"
          class="material-item"
        >
          <view class="material-dot"></view>
          <view class="material-text">{{ m }}</view>
        </view>
      </view>
    </view>

    <!-- 步骤列表 -->
    <view class="section">
      <view class="section-title">👨‍🍳 做法步骤</view>
      <view class="step-box">
        <view
          v-for="(s, i) in steps"
          :key="i"
          class="step-item"
        >
          <view class="step-num">{{ i + 1 }}</view>
          <view class="step-text">{{ s }}</view>
        </view>
      </view>
    </view>

    <!-- 小贴士 -->
    <view v-if="recipe.tip" class="section">
      <view class="section-title">💡 小贴士</view>
      <view class="tip-box">{{ recipe.tip }}</view>
    </view>

    <view class="bottom-space"></view>

    <!-- 底部"投它一票"按钮 -->
    <view class="bottom-bar">
      <view class="btn btn-primary btn-block big-btn" @tap="voteIt">
        🎯 投它一票
      </view>
    </view>
  </view>

  <view v-else class="loading-page">
    <text class="loading-icon">🍽️</text>
    <view>加载中...</view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import Taro, { useRouter } from "@tarojs/taro";
import { getRecipe } from "@/api/recipe";
import type { Recipe } from "@/types";

const router = useRouter();
const id = parseInt(router.params.id || "0");

const defaultCover = "https://img.icons8.com/color/96/dinner.png";

const recipe = ref<Recipe | null>(null);

// material / step 后端存的是 \n 分隔的字符串
const materials = computed(() => {
  const s = recipe.value?.material || "";
  return s.split(/\n/).map((x) => x.trim()).filter(Boolean);
});
const steps = computed(() => {
  const s = recipe.value?.step || "";
  return s.split(/\n/).map((x) => x.trim()).filter(Boolean);
});

async function load() {
  if (!id) {
    Taro.showToast({ title: "参数错误", icon: "none" });
    Taro.navigateBack();
    return;
  }
  try {
    const res = await getRecipe(id);
    recipe.value = res.data;
    Taro.setNavigationBarTitle({ title: res.data.title || "菜谱详情" });
  } catch {
    Taro.showToast({ title: "加载失败", icon: "none" });
  }
}

function voteIt() {
  // 跳到投票 tab，选中这个菜谱
  Taro.switchTab({ url: "/pages/vote/vote" });
  // 用 eventChannel 或者 storage 简单传一下选中的 id
  Taro.setStorageSync("vote_preselect_id", id);
}

onMounted(load);
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page { padding-bottom: 180px; position: relative; }

/* ===== 封面 ===== */
.cover {
  width: 100%;
  height: 500px;
  background: #FFF0E6;
  position: relative;
}
.cover-shade {
  position: absolute;
  top: 0; left: 0; right: 0; height: 200px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.35), transparent);
  pointer-events: none;
}

/* ===== 标题框 ===== */
.title-box {
  margin: -60px 24px 0;
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  box-shadow: $card-shadow;
  position: relative;
  z-index: 10;
}
.recipe-title {
  font-size: 40px;
  font-weight: 800;
  color: #222;
  margin-bottom: 14px;
}
.recipe-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.meta-item { font-size: 24px; color: #888; }

/* ===== 区块 ===== */
.section { margin-top: 28px; }
.material-box {
  margin: 0 24px;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: $card-shadow;
}
.material-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #FFE0D6;

  &:last-child { border-bottom: none; }
}
.material-dot {
  width: 14px; height: 14px;
  border-radius: 50%;
  background: $primary;
  margin-top: 12px;
  margin-right: 16px;
  flex-shrink: 0;
}
.material-text { font-size: 28px; color: #333; flex: 1; }

.step-box {
  margin: 0 24px;
  background: #fff;
  border-radius: 16px;
  padding: 16px 24px;
  box-shadow: $card-shadow;
}
.step-item {
  display: flex;
  gap: 18px;
  padding: 18px 0;
  border-bottom: 1px solid #FFE0D6;

  &:last-child { border-bottom: none; }
}
.step-num {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: $bg-gradient;
  color: #fff;
  font-weight: 700;
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(255, 45, 45, 0.25);
}
.step-text { font-size: 28px; color: #333; flex: 1; line-height: 1.6; }

.tip-box {
  margin: 0 24px;
  background: linear-gradient(135deg, #FFF9E6, #FFF5CC);
  border-left: 6px solid $yellow;
  border-radius: 0 12px 12px 0;
  padding: 24px;
  font-size: 26px;
  color: #666;
  line-height: 1.8;
}

.bottom-space { height: 40px; }

/* ===== 底部按钮 ===== */
.bottom-bar {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  padding: 16px 24px 40px;
  background: linear-gradient(to top, #FFF5F0 70%, transparent);
  z-index: 50;
}
.big-btn {
  padding: 26px;
  font-size: 32px;
  font-weight: 800;
}

/* ===== 加载 ===== */
.loading-page {
  padding: 200px 0;
  text-align: center;
  color: #999;
}
.loading-icon { font-size: 80px; display: block; margin-bottom: 16px; }
</style>
