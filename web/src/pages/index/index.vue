<template>
  <view class="page">
    <!-- ===== 1. 顶部栏（红橙渐变） ===== -->
    <view class="hero">
      <view class="hero-title">🍳 今天吃什么</view>
      <view class="hero-sub">每日抽签 · 闪购限时</view>
    </view>

    <!-- ===== 2. 搜索栏（圆角白色 + 热点标签） ===== -->
    <view class="search-bar">
      <view class="search-input-wrap" @tap="focusSearch">
        <text class="search-icon">🔍</text>
        <text class="search-placeholder">{{ keyword || '搜索菜谱...' }}</text>
      </view>
      <view v-if="hotKeyword" class="hot-tag" @tap="onTapHotTag">
        <text class="hot-fire">🔥</text>
        <text class="hot-text">{{ hotKeyword }}</text>
      </view>
    </view>

    <!-- ===== 3. 分类标签（横向滚动） ===== -->
    <scroll-view scroll-x class="cate-scroll" enhanced :show-scrollbar="false">
      <view class="cate-inner">
        <view
          v-for="c in categories"
          :key="c.id"
          class="cate-item"
          :class="{ active: currentCategoryId === c.id }"
          @tap="selectCategory(c.id)"
        >
          {{ c.name }}
        </view>
      </view>
    </scroll-view>

    <!-- ===== 4. 横滑大卡片：🔥 热门推荐 ===== -->
    <view v-if="hotList.length > 0" class="section-title">🔥 热门推荐</view>
    <scroll-view v-if="hotList.length > 0" scroll-x class="hot-scroll" enhanced :show-scrollbar="false">
      <view class="hot-inner">
        <view
          v-for="r in hotList"
          :key="'hot-' + r.id"
          class="hot-card"
          @tap="goDetail(r.id)"
        >
          <image class="hot-cover" :src="r.cover_img || defaultCover" mode="aspectFill" />
          <view class="hot-info">
            <view class="hot-title">{{ r.title }}</view>
            <view class="hot-meta">
              <text class="badge-tag">{{ r.category_name || '家常菜' }}</text>
              <text class="hot-time">⏱ {{ r.cook_time || '30分钟' }}</text>
            </view>
            <view class="hot-btn">✨ 去看看</view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- ===== 5. 网格卡片：两列菜谱列表 ===== -->
    <view class="section-title">📋 全部菜谱</view>
    <view class="recipe-grid">
      <view
        v-for="r in recipeList"
        :key="'recipe-' + r.id"
        class="recipe-card"
        @tap="goDetail(r.id)"
      >
        <image class="recipe-cover" :src="r.cover_img || defaultCover" mode="aspectFill" />
        <view class="recipe-info">
          <view class="recipe-title">{{ r.title }}</view>
          <view class="recipe-meta">
            <text class="badge-tag">{{ r.category_name || '家常菜' }}</text>
            <text class="recipe-time">⏱ {{ r.cook_time || '-' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ===== 6. 空状态 ===== -->
    <view v-if="recipeList.length === 0 && !loading" class="empty">
      <text class="empty-icon">🍽️</text>
      <view>暂无菜谱，快去添加吧</view>
    </view>

    <view class="footer-tip">—— 今天吃什么，由闪购给你答案 ——</view>
  </view>
</template>

<script setup lang="ts">
// ===== 保持原有 import + 补充分类接口 =====
import { ref, onMounted } from 'vue';
import Taro from '@tarojs/taro';
import { listRecipes } from '@/api/recipe';
import { listCategories } from '@/api/category';
import type { Recipe, Category } from '@/types';

// ===== 默认封面（emoji fallback） =====
const defaultCover = 'https://img.icons8.com/color/96/dinner.png';

// ===== 离线兜底数据（API 不通时用） =====
const MOCK_CATEGORIES: Category[] = [
  { id: 0, name: '全部' },
  { id: 1, name: '家常菜' },
  { id: 2, name: '快手菜' },
  { id: 3, name: '硬菜' },
  { id: 4, name: '汤品' },
  { id: 5, name: '素菜' },
  { id: 6, name: '主食' },
];

const MOCK_RECIPES: Recipe[] = [
  { id: 1, title: '番茄炒蛋', material: '番茄2个,鸡蛋3个', step: '鸡蛋打散，炒番茄出汁，倒回鸡蛋翻炒', tip: '酸甜开胃', cover_img: 'https://picsum.photos/seed/tomato1/400/300', category_id: 1, category_name: '家常菜', cook_time: '15分钟', views: 99 },
  { id: 2, title: '红烧肉', material: '五花肉500g,冰糖30g', step: '焯水→炒糖色→炖60分钟→收汁', tip: '肥而不腻', cover_img: 'https://picsum.photos/seed/pork1/400/300', category_id: 3, category_name: '硬菜', cook_time: '90分钟', views: 88 },
  { id: 3, title: '青椒土豆丝', material: '土豆2个,青椒1个', step: '切丝泡水→爆香蒜末→快炒', tip: '清脆爽口', cover_img: 'https://picsum.photos/seed/potato1/400/300', category_id: 2, category_name: '快手菜', cook_time: '10分钟', views: 77 },
  { id: 4, title: '糖醋排骨', material: '排骨500g,冰糖30g', step: '焯水→炒糖色→炖30分钟→收汁', tip: '外酥里嫩', cover_img: 'https://picsum.photos/seed/ribs1/400/300', category_id: 3, category_name: '硬菜', cook_time: '60分钟', views: 66 },
  { id: 5, title: '可乐鸡翅', material: '鸡翅中8个,可乐1罐', step: '划刀→煎金黄→倒可乐→收汁', tip: '新手零失败', cover_img: 'https://picsum.photos/seed/wings1/400/300', category_id: 3, category_name: '硬菜', cook_time: '40分钟', views: 55 },
  { id: 6, title: '蛋炒饭', material: '米饭1碗,鸡蛋2个', step: '鸡蛋炒散→加米饭→加盐', tip: '剩米饭的变身', cover_img: 'https://picsum.photos/seed/rice1/400/300', category_id: 6, category_name: '主食', cook_time: '10分钟', views: 44 },
  { id: 7, title: '番茄蛋汤', material: '番茄1个,鸡蛋1个', step: '炒番茄→加水→淋蛋液', tip: '营养丰富', cover_img: 'https://picsum.photos/seed/soup1/400/300', category_id: 4, category_name: '汤品', cook_time: '10分钟', views: 33 },
  { id: 8, title: '蒜蓉西兰花', material: '西兰花1颗,蒜5瓣', step: '焯水→爆香蒜末→快炒', tip: '清淡健康', cover_img: 'https://picsum.photos/seed/broccoli1/400/300', category_id: 5, category_name: '素菜', cook_time: '5分钟', views: 22 },
  { id: 9, title: '酸辣土豆丝', material: '土豆2个,干辣椒3个', step: '切丝泡水→爆香→快炒→加醋', tip: '5分钟搞定', cover_img: 'https://picsum.photos/seed/potato2/400/300', category_id: 2, category_name: '快手菜', cook_time: '8分钟', views: 11 },
  { id: 10, title: '紫菜蛋花汤', material: '紫菜1小把,鸡蛋1个', step: '水烧开→下紫菜→淋蛋液', tip: '清淡鲜美', cover_img: 'https://picsum.photos/seed/soup2/400/300', category_id: 4, category_name: '汤品', cook_time: '8分钟', views: 10 },
  { id: 11, title: '地三鲜', material: '茄子1个,土豆1个,青椒1个', step: '切块分别炸→调汁翻炒', tip: '东北名菜', cover_img: 'https://picsum.photos/seed/veg1/400/300', category_id: 1, category_name: '家常菜', cook_time: '25分钟', views: 9 },
  { id: 12, title: '葱花鸡蛋饼', material: '面粉100g,鸡蛋2个', step: '面糊搅匀→平底锅摊饼', tip: '早餐5分钟', cover_img: 'https://picsum.photos/seed/pancake1/400/300', category_id: 6, category_name: '主食', cook_time: '10分钟', views: 8 },
  { id: 13, title: '蛋炒面', material: '面条1把,鸡蛋2个', step: '煮面→炒蛋→加面翻炒', tip: '深夜食堂', cover_img: 'https://picsum.photos/seed/noodle1/400/300', category_id: 6, category_name: '主食', cook_time: '15分钟', views: 7 },
  { id: 14, title: '清炒时蔬', material: '青菜1把,蒜2瓣', step: '热油爆蒜→下青菜快炒', tip: '最简单的美味', cover_img: 'https://picsum.photos/seed/veg2/400/300', category_id: 5, category_name: '素菜', cook_time: '5分钟', views: 6 },
];

// ===== 响应式数据 =====
const loading = ref(false);                // 全局加载状态
const keyword = ref('');                  // 搜索关键词
const hotKeyword = ref('');               // 🔥 热点菜名（从热门列表随机取）
const currentCategoryId = ref<number>(0); // 当前分类 id，0 表示"全部"
const hotList = ref<Recipe[]>([]);        // 🔥 热门推荐（views 最多的 5 条）
const recipeList = ref<Recipe[]>([]);     // 📋 全部菜谱（网格）
const categories = ref<Category[]>([      // 分类列表（带"全部"）
  { id: 0, name: '全部' } as Category,
]);

// ===== Toast 提示（使用 Taro.showToast） =====
function showToast(title: string) {
  Taro.showToast({ title, icon: 'none', duration: 1500 });
}

// ===== 从 mock 数据筛选（分类 + 关键词） =====
function filterMock(): Recipe[] {
  let list = [...MOCK_RECIPES];
  if (currentCategoryId.value && currentCategoryId.value !== 0) {
    list = list.filter(r => r.category_id === currentCategoryId.value);
  }
  if (keyword.value) {
    list = list.filter(r => r.title.includes(keyword.value!));
  }
  return list;
}

// ===== 加载分类列表（失败用 mock） =====
async function loadCategories() {
  try {
    const res = await listCategories();
    if (res.code === 200 && Array.isArray(res.data)) {
      categories.value = [
        { id: 0, name: '全部' } as Category,
        ...res.data,
      ];
      return;
    }
  } catch (e) {}
  // 兜底
  categories.value = MOCK_CATEGORIES;
}

// ===== 加载 🔥 热门推荐（失败用 mock） =====
async function loadHot() {
  try {
    const res = await listRecipes({ page: 1, per_page: 8 });
    if (res.code === 200) {
      const items: Recipe[] = res.data?.items || [];
      const sorted = [...items].sort(
        (a, b) => (b.views || 0) - (a.views || 0)
      );
      hotList.value = sorted.slice(0, 5);
      if (hotList.value.length > 0) {
        const pick = hotList.value[Math.floor(Math.random() * hotList.value.length)];
        hotKeyword.value = pick.title || '';
      }
      return;
    }
  } catch (e) {}
  // 兜底：mock 里按 views 取前 5
  const sorted = [...MOCK_RECIPES].sort((a, b) => (b.views || 0) - (a.views || 0));
  hotList.value = sorted.slice(0, 5);
  hotKeyword.value = hotList.value[Math.floor(Math.random() * hotList.value.length)].title;
}

// ===== 加载 📋 网格菜谱（失败用 mock） =====
async function loadAll() {
  loading.value = true;
  try {
    const res = await listRecipes({
      page: 1,
      per_page: 20,
      category_id: currentCategoryId.value || undefined,
      keyword: keyword.value || undefined,
    });
    if (res.code === 200) {
      recipeList.value = res.data?.items || [];
      if (recipeList.value.length > 0) return;
    }
  } catch (e) {}
  // 兜底
  recipeList.value = filterMock();
}

// ===== 点击分类标签 =====
function selectCategory(id: number) {
  currentCategoryId.value = id;
  loadAll();
}

// ===== 搜索栏点击 =====
function focusSearch() {
  Taro.showModal({
    title: '搜索菜谱',
    content: '在下方控制台或直接点击 🔥 热点标签搜索',
    showCancel: false,
    confirmText: '知道了',
  });
}

// ===== 点击 🔥 热点标签：把它当作关键词搜索 =====
function onTapHotTag() {
  if (hotKeyword.value) {
    keyword.value = hotKeyword.value;
    loadAll();
  }
}

// ===== 跳转到菜谱详情 =====
function goDetail(id: number) {
  Taro.navigateTo({ url: `/pages/recipe/detail?id=${id}` });
}

// ===== 生命周期：首次进入加载全部 =====
onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([loadCategories(), loadHot(), loadAll()]);
  } finally {
    loading.value = false;
  }
});
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page {
  padding-bottom: 60px;
  background: #FFF5F0;
  min-height: 100vh;
}

/* ===== 顶部 Hero：红橙渐变 ===== */
.hero {
  background: $bg-gradient;
  padding: 60px 40px 48px;
  text-align: center;
  border-bottom-left-radius: 32px;
  border-bottom-right-radius: 32px;
  box-shadow: 0 8px 32px rgba(255, 45, 45, 0.2);

  .hero-title {
    font-size: 56px;
    font-weight: 800;
    color: #fff;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  .hero-sub {
    font-size: 26px;
    color: rgba(255, 255, 255, 0.92);
    margin-top: 8px;
    letter-spacing: 4px;
  }
}

/* ===== 搜索栏 ===== */
.search-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: -20px 24px 16px;
  position: relative;
  z-index: 10;
}
.search-input-wrap {
  flex: 1;
  background: #fff;
  height: 72px;
  border-radius: 40px;
  padding: 0 28px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.search-icon { font-size: 28px; }
.search-placeholder {
  font-size: 28px;
  color: #bbb;
  flex: 1;
}
.hot-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #FFF0E6, #FFDCC8);
  padding: 0 18px;
  height: 72px;
  border-radius: 40px;
  font-size: 24px;
  color: $primary;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(255, 106, 0, 0.15);
  max-width: 260px;
  overflow: hidden;
}
.hot-fire { font-size: 28px; }
.hot-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

/* ===== 分类标签横向滚动 ===== */
.cate-scroll {
  width: 100%;
  white-space: nowrap;
  padding: 4px 0 8px;
}
.cate-inner {
  display: inline-flex;
  gap: 16px;
  padding: 4px 24px;
}
.cate-item {
  display: inline-block;
  padding: 12px 28px;
  font-size: 28px;
  color: #666;
  background: #fff;
  border-radius: 32px;
  border: 2px solid transparent;
  transition: all 0.2s;

  &.active {
    color: #fff;
    background: $bg-gradient;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(255, 45, 45, 0.25);
  }
}

/* ===== 热门推荐横滑大卡片 ===== */
.hot-scroll { width: 100%; white-space: nowrap; padding: 0 8px; }
.hot-inner {
  display: inline-flex;
  padding: 0 16px;
  gap: 20px;
}
.hot-card {
  display: inline-block;
  width: 400px;
  background: #fff;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: $card-shadow;
  white-space: normal;
  vertical-align: top;
}
.hot-cover {
  width: 100%;
  height: 240px;
  background: #FFF0E6;
}
.hot-info { padding: 20px; }
.hot-title {
  font-size: 30px;
  font-weight: 700;
  color: #222;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hot-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.hot-time { font-size: 24px; color: #999; }
.hot-btn {
  text-align: center;
  background: $bg-gradient;
  color: #fff;
  font-weight: 600;
  font-size: 26px;
  padding: 14px 0;
  border-radius: 12px;
}

/* ===== 菜谱网格（两列） ===== */
.recipe-grid {
  padding: 0 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
}
.recipe-card {
  width: calc(50% - 9px);
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: $card-shadow;
}
.recipe-cover {
  width: 100%;
  height: 200px;
  background: #FFF0E6;
}
.recipe-info { padding: 16px; }
.recipe-title {
  font-size: 28px;
  font-weight: 600;
  color: #222;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recipe-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.recipe-time { font-size: 22px; color: #999; }

/* ===== 空状态 ===== */
.empty {
  text-align: center;
  padding: 160px 40px;
  color: #999;

  .empty-icon {
    font-size: 120px;
    display: block;
    margin-bottom: 20px;
  }
}

/* ===== 底部提示 ===== */
.footer-tip {
  text-align: center;
  color: #ccc;
  font-size: 22px;
  padding: 40px 0 20px;
}
</style>
