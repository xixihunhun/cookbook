<template>
  <view class="page">
    <!-- 大标题 + 日期 -->
    <view class="vote-hero">
      <view class="vote-title">🎲 今日吃啥？</view>
      <view class="vote-date">{{ todayStr }}</view>
      <view v-if="familyName" class="vote-family">🏠 {{ familyName }} 的投票</view>
    </view>

    <!-- 没登录 → 引导登录 -->
    <view v-if="!isLoggedIn" class="card guide-card">
      <view class="guide-icon">🔐</view>
      <view class="guide-title">请先登录</view>
      <view class="guide-sub">登录后才能和家人一起投票哦</view>
      <view class="btn btn-primary btn-block" @tap="goLogin">立即登录</view>
    </view>

    <!-- 已登录 但没家庭 → 引导绑定 -->
    <view v-else-if="!familyId" class="card guide-card">
      <view class="guide-icon">🏠</view>
      <view class="guide-title">你还没加入家庭</view>
      <view class="guide-sub">创建或加入一个家庭，开始每日投票</view>
      <view class="btn btn-primary btn-block" @tap="goBind">去绑定家庭</view>
    </view>

    <!-- 已登录 + 有家庭 -->
    <block v-else>
      <!-- 投票剩余时间 -->
      <view class="countdown-bar" v-if="!voted">
        <text>🕐 投票剩余</text>
        <text class="countdown-num">{{ cd.h }}</text>
        <text>:</text>
        <text class="countdown-num">{{ cd.m }}</text>
        <text>:</text>
        <text class="countdown-num">{{ cd.s }}</text>
        <text class="voted-count">已投 {{ todayData?.voted_count || 0 }}/2</text>
      </view>

      <!-- 未投票：候选池网格 -->
      <block v-if="!voted">
        <view class="section-title">🔥 今日候选菜谱（点我选一个）</view>
        <view class="recipe-grid">
          <view
            v-for="r in candidates"
            :key="r.id"
            class="vote-card"
            :class="{ selected: selectedId === r.id }"
            @tap="selectOne(r.id)"
          >
            <image class="vote-cover" :src="r.cover_img || defaultCover" mode="aspectFill" />
            <view class="vote-info">
              <view class="vote-name">{{ r.title }}</view>
              <view class="vote-meta">
                <text class="badge-tag">{{ r.category_name || '家常菜' }}</text>
                <text class="vote-time">⏱ {{ r.cook_time || '30分钟' }}</text>
              </view>
            </view>
            <view v-if="selectedId === r.id" class="check-mark">✓</view>
          </view>
        </view>
        <view v-if="candidates.length === 0 && !loading" class="empty">
          <text class="empty-icon">🍽️</text>
          <view>今日候选池还没准备好</view>
        </view>

        <!-- 底部大按钮 -->
        <view class="bottom-action">
          <view
            class="btn btn-primary btn-block big-btn"
            :class="{ disabled: !selectedId || casting }"
            @tap="doCast"
          >
            {{ casting ? '投票中...' : '✨ 就吃它了！投票' }}
          </view>
        </view>
      </block>

      <!-- 已投票：展示结果 -->
      <block v-else>
        <view class="result-card">
          <!-- 达成一致 -->
          <block v-if="agreed">
            <view class="agree-banner">🎉 达成一致！今天就吃这个！🎉</view>
            <view class="winner-card">
              <image
                class="winner-cover"
                :src="(myVote && myVote.recipe_id === partnerVote?.recipe_id
                  ? candidateCover(myVote.recipe_id)
                  : '') || defaultCover"
                mode="aspectFill"
              />
              <view class="winner-title">{{ myVote?.recipe_title || '今日菜谱' }}</view>
              <view class="winner-both">你和家人都投了它 👫</view>
            </view>
          </block>

          <!-- 意见不一致 -->
          <block v-else>
            <view class="disagree-banner">🤔 意见不一致，再投一次！</view>
            <view class="compare-row">
              <view class="compare-item mine">
                <text class="compare-label">👤 你投的</text>
                <text class="compare-name">{{ myVote?.recipe_title || '-' }}</text>
              </view>
              <view class="vs-badge">VS</view>
              <view class="compare-item partner">
                <text class="compare-label">💑 TA 投的</text>
                <text class="compare-name">{{ partnerVote?.recipe_title || '-' }}</text>
              </view>
            </view>
            <view class="btn btn-primary btn-block" @tap="switchToRevote">🔄 点我改投</view>
          </block>
        </view>
      </block>

      <!-- 历史记录按钮 -->
      <view class="history-btn" @tap="toggleHistory">
        📊 历史记录 <text class="arrow">{{ showHistory ? '▲' : '▼' }}</text>
      </view>

      <view v-if="showHistory" class="history-list">
        <view v-if="historyItems.length === 0" class="empty small">暂无历史</view>
        <view v-for="h in historyItems" :key="h.vote_date" class="history-item">
          <view class="h-date">{{ h.vote_date }}</view>
          <view class="h-detail">
            <text class="badge-tag">{{ h.agreed ? '✅ 一致' : '❌ 不一致' }}</text>
            <text v-if="h.winner_recipe" class="h-winner">→ {{ h.winner_recipe.title }}</text>
          </view>
        </view>
      </view>
    </block>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import Taro, { useDidShow } from "@tarojs/taro";
import { recommend, castVote, todayResult, history as voteHistory } from "@/api/vote";
import type { Recipe, VoteTodayResult, VoteHistoryItem } from "@/types";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const { isLoggedIn, familyId, familyName } = userStore;

const defaultCover = "https://img.icons8.com/color/96/dinner.png";

const candidates = ref<Recipe[]>([]);
const todayData = ref<VoteTodayResult | null>(null);
const historyItems = ref<VoteHistoryItem[]>([]);
const loading = ref(false);
const casting = ref(false);
const selectedId = ref<number | null>(null);
const showHistory = ref(false);

const todayStr = new Date().toLocaleDateString("zh-CN", {
  year: "numeric", month: "long", day: "numeric", weekday: "long",
});

// 派生：我是否已投票
const voted = computed(() => !!todayData.value?.my_vote);
const myVote = computed(() => todayData.value?.my_vote);
const partnerVote = computed(() => todayData.value?.partner_vote);
const agreed = computed(() => todayData.value?.agreed === true);

// 倒计时（用后端给的 deadline_ts 优先，没有就用本地 23:59:59）
const cd = reactive({ h: "00", m: "00", s: "00" });
let cdTimer: number | null = null;

function pad(n: number) { return String(n).padStart(2, "0"); }

function startCountdown() {
  const update = () => {
    let deadlineMs: number;
    const ts = todayData.value?.deadline_ts;
    if (ts && ts > 0) {
      deadlineMs = ts * 1000;
    } else {
      const d = new Date();
      d.setHours(23, 59, 59, 999);
      deadlineMs = d.getTime();
    }
    const diff = Math.max(0, Math.floor((deadlineMs - Date.now()) / 1000));
    cd.h = pad(Math.floor(diff / 3600));
    cd.m = pad(Math.floor((diff % 3600) / 60));
    cd.s = pad(diff % 60);
  };
  update();
  cdTimer = setInterval(update, 1000) as any;
}

function candidateCover(id: number) {
  return candidates.value.find((c) => c.id === id)?.cover_img || "";
}

async function loadAll() {
  if (!isLoggedIn) return;
  if (!familyId) return;
  loading.value = true;
  try {
    const [rec, td] = await Promise.all([
      recommend().catch(() => ({ data: [] as Recipe[] })),
      todayResult(),
    ]);
    candidates.value = (rec as any).data || [];
    todayData.value = (td as any).data;
    // 默认选中：如果我已投过，预选我自己的
    if (todayData.value?.my_vote) {
      selectedId.value = todayData.value.my_vote.recipe_id;
    } else {
      selectedId.value = candidates.value[0]?.id ?? null;
    }
    startCountdown();
  } catch (e: any) {
    Taro.showToast({ title: e?.message || "加载失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

function selectOne(id: number) {
  selectedId.value = id;
}

async function doCast() {
  if (!selectedId.value || casting.value) return;
  casting.value = true;
  try {
    const res = await castVote(selectedId.value);
    todayData.value = res.data;
    Taro.showToast({
      title: agreed.value ? "🎉 达成一致！" : "✅ 投票成功",
      icon: "none",
    });
    loadHistory();
  } catch {} finally {
    casting.value = false;
  }
}

function switchToRevote() {
  selectedId.value = null;
  todayData.value = null; // 清空，重新走未投票 UI
  // 但其实 loadAll 会重拉；简单处理：重载一次
  loadAll();
}

async function loadHistory() {
  try {
    const res = await voteHistory(7);
    historyItems.value = (res as any).data || [];
  } catch {}
}

function toggleHistory() {
  showHistory.value = !showHistory.value;
  if (showHistory.value && historyItems.value.length === 0) loadHistory();
}

function goLogin() { Taro.navigateTo({ url: "/pages/login/index" }); }
function goBind() { Taro.navigateTo({ url: "/pages/family/bind" }); }

onMounted(loadAll);
useDidShow(() => {
  // 每次从后台切回都刷新（比如登录后回来）
  loadAll();
});
onUnmounted(() => {
  if (cdTimer) clearInterval(cdTimer);
});
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page { padding-bottom: 120px; }

/* ===== Hero ===== */
.vote-hero {
  background: $bg-gradient;
  padding: 50px 40px 40px;
  text-align: center;
  border-bottom-left-radius: 32px;
  border-bottom-right-radius: 32px;
  box-shadow: 0 8px 32px rgba(255, 45, 45, 0.2);
}
.vote-title {
  font-size: 52px;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
.vote-date {
  font-size: 28px;
  color: rgba(255, 255, 255, 0.95);
  margin-top: 6px;
}
.vote-family {
  display: inline-block;
  margin-top: 16px;
  padding: 6px 24px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  font-size: 24px;
  color: #fff;
}

/* ===== 引导卡片 ===== */
.guide-card { text-align: center; padding: 60px 40px; }
.guide-icon { font-size: 120px; margin-bottom: 16px; }
.guide-title { font-size: 36px; font-weight: 700; color: #222; }
.guide-sub { font-size: 26px; color: #888; margin: 12px 0 32px; }

/* ===== 已投人数 ===== */
.voted-count {
  margin-left: 16px;
  padding: 4px 14px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  font-size: 22px;
}

/* ===== 候选网格 ===== */
.recipe-grid {
  padding: 0 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
}
.vote-card {
  position: relative;
  width: calc(50% - 9px);
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: $card-shadow;
  border: 3px solid transparent;
  transition: transform 0.15s, border-color 0.15s;

  &:active { transform: scale(0.97); }
  &.selected {
    border-color: $primary;
    box-shadow: 0 0 0 3px rgba(255, 45, 45, 0.2), $card-shadow;
  }
}
.vote-cover { width: 100%; height: 220px; background: #FFF0E6; }
.vote-info { padding: 16px; }
.vote-name {
  font-size: 28px;
  font-weight: 700;
  color: #222;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.vote-meta { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.vote-time { font-size: 22px; color: #999; }
.check-mark {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 50px;
  height: 50px;
  background: $bg-gradient;
  color: #fff;
  font-size: 34px;
  font-weight: 700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 45, 45, 0.4);
}

/* ===== 底部大按钮 ===== */
.bottom-action {
  position: fixed;
  left: 0; right: 0; bottom: 0;
  padding: 20px 24px 40px;
  background: linear-gradient(to top, #FFF5F0 70%, transparent);
  z-index: 50;
}
.big-btn {
  padding: 30px;
  font-size: 34px;
  font-weight: 800;

  &.disabled {
    opacity: 0.5;
  }
}

/* ===== 结果卡片 ===== */
.result-card {
  margin: 24px;
  background: #fff;
  border-radius: 24px;
  padding: 32px;
  box-shadow: $card-shadow;
}
.agree-banner {
  text-align: center;
  font-size: 36px;
  font-weight: 800;
  color: $primary;
  padding: 20px;
  background: linear-gradient(135deg, #FFF0E6, #FFE4CC);
  border-radius: 16px;
  margin-bottom: 24px;
}
.disagree-banner {
  text-align: center;
  font-size: 30px;
  font-weight: 700;
  color: #FF6A00;
  padding: 16px;
  background: #FFF9F0;
  border-radius: 16px;
  margin-bottom: 24px;
}
.winner-card { text-align: center; }
.winner-cover {
  width: 100%;
  height: 360px;
  border-radius: 20px;
  background: #FFF0E6;
  margin-bottom: 20px;
}
.winner-title {
  font-size: 38px;
  font-weight: 800;
  color: #222;
}
.winner-both {
  font-size: 26px;
  color: #888;
  margin-top: 8px;
}

.compare-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}
.compare-item {
  flex: 1;
  padding: 20px 16px;
  border-radius: 16px;
  text-align: center;

  &.mine { background: #FFF0E6; }
  &.partner { background: #E6F0FF; }
}
.compare-label {
  display: block;
  font-size: 22px;
  color: #888;
  margin-bottom: 6px;
}
.compare-name {
  font-size: 28px;
  font-weight: 700;
  color: #222;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.vs-badge {
  font-size: 28px;
  font-weight: 800;
  color: $primary;
  padding: 8px;
}

/* ===== 历史 ===== */
.history-btn {
  margin: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 16px;
  text-align: center;
  font-size: 28px;
  color: #666;
  box-shadow: $card-shadow;
}
.history-list { padding: 0 24px; }
.history-item {
  background: #fff;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 12px;
  box-shadow: $card-shadow;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.h-date { font-size: 28px; color: #222; font-weight: 600; }
.h-detail { display: flex; align-items: center; gap: 8px; }
.h-winner { font-size: 24px; color: #888; }

.empty.small { padding: 40px; font-size: 26px; }
</style>
