<template>
  <view class="page">
    <!-- 没家庭 -->
    <view v-if="!family" class="card empty-card">
      <view class="empty-icon">🏠</view>
      <view class="empty-title">你还没加入家庭</view>
      <view class="empty-sub">创建或加入一个家庭吧</view>
      <view class="btn btn-primary btn-block" @tap="goBind">去绑定</view>
    </view>

    <!-- 有家庭 -->
    <block v-else>
      <view class="card family-card">
        <view class="fc-title">🏡 当前家庭</view>
        <view class="fc-name">{{ family.name }}</view>

        <view class="fc-code-row">
          <text class="fc-code-label">邀请码</text>
          <view class="fc-code">{{ family.invite_code }}</view>
          <view class="fc-copy" @tap="copyCode">复制</view>
        </view>

        <view class="divider"></view>

        <view class="fc-members-title">家庭成员（{{ family.members.length }} 人）</view>
        <view
          v-for="m in family.members"
          :key="m.id"
          class="fc-member"
        >
          <image class="fc-avatar" :src="m.avatar || defaultAvatar" mode="aspectFill" />
          <view class="fc-nickname">
            {{ m.nickname }}
            <text v-if="m.is_creator" class="badge-hot" style="margin-left:8px">房主</text>
            <text v-if="m.user_id === myId" class="badge-tag" style="margin-left:8px">我</text>
          </view>
        </view>
      </view>

      <view class="btn btn-danger btn-block" @tap="doLeave">退出家庭</view>
    </block>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onShow } from "vue";
import Taro from "@tarojs/taro";
import { leaveFamily, getMyFamily } from "@/api/family";
import type { Family } from "@/types";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const { user, setFamily } = userStore;

const defaultAvatar = "https://img.icons8.com/color/96/user-male-circle--v1.png";

const family = ref<Family | null>(null);
const myId = computed(() => userStore.user?.id ?? 0);

async function load() {
  try {
    const res = await getMyFamily();
    family.value = res.data || null;
    setFamily(family.value);
  } catch {}
}

async function copyCode() {
  if (!family.value) return;
  await Taro.setClipboardData({ data: family.value.invite_code });
  Taro.showToast({ title: "已复制", icon: "none" });
}

async function doLeave() {
  Taro.showModal({
    title: "确认退出",
    content: "退出后将无法参与家庭投票，确定吗？",
    success: async (r) => {
      if (!r.confirm) return;
      try {
        await leaveFamily();
        family.value = null;
        setFamily(null);
        Taro.showToast({ title: "已退出", icon: "none" });
      } catch {}
    },
  });
}

function goBind() { Taro.navigateTo({ url: "/pages/family/bind" }); }

onMounted(load);
onShow(load);
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page { padding: 24px; }

.empty-card { text-align: center; padding: 80px 40px; }
.empty-icon { font-size: 140px; margin-bottom: 20px; }
.empty-title { font-size: 36px; font-weight: 700; color: #222; }
.empty-sub { font-size: 26px; color: #999; margin: 12px 0 32px; }

.family-card { padding: 32px; }
.fc-title { font-size: 26px; color: #888; margin-bottom: 6px; }
.fc-name { font-size: 48px; font-weight: 800; color: #222; margin-bottom: 24px; }
.fc-code-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #FFF0E6;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 16px;
}
.fc-code-label { font-size: 24px; color: #888; }
.fc-code {
  flex: 1;
  font-family: "Menlo", "Courier New", monospace;
  font-size: 32px;
  font-weight: 700;
  color: $primary;
  letter-spacing: 4px;
}
.fc-copy {
  padding: 8px 20px;
  background: $primary;
  color: #fff;
  border-radius: 12px;
  font-size: 24px;
  font-weight: 600;
}
.fc-members-title { font-size: 28px; font-weight: 600; color: #333; margin-bottom: 16px; }
.fc-member {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #FFE0D6;

  &:last-child { border-bottom: none; }
}
.fc-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: #FFF0E6;
}
.fc-nickname { font-size: 28px; color: #222; font-weight: 600; }
</style>
