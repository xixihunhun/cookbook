<template>
  <view class="page">
    <!-- 顶部标题 -->
    <view class="hero">
      <view class="hero-title">🏠 家庭绑定</view>
      <view class="hero-sub">两个人，一个家，一起决定今天吃啥</view>
    </view>

    <!-- 没家庭 -->
    <block v-if="!family">
      <!-- 两个大按钮卡片 -->
      <view class="action-card" @tap="showCreate = true">
        <view class="action-icon">🏠</view>
        <view class="action-body">
          <view class="action-title">创建家庭</view>
          <view class="action-sub">新建一个家庭，生成邀请码给另一半</view>
        </view>
        <view class="action-arrow">›</view>
      </view>

      <view class="action-card" @tap="showJoin = true">
        <view class="action-icon">🔑</view>
        <view class="action-body">
          <view class="action-title">输入邀请码加入</view>
          <view class="action-sub">另一半已经创建好了，输入邀请码加入</view>
        </view>
        <view class="action-arrow">›</view>
      </view>

      <!-- 创建弹窗 -->
      <view v-if="showCreate" class="mask" @tap.self="showCreate = false">
        <view class="modal">
          <view class="modal-title">🏠 创建家庭</view>
          <view class="form-item">
            <view class="form-label">家庭名称</view>
            <input
              class="input"
              v-model="createName"
              placeholder="比如：温馨小家"
              maxlength="12"
            />
          </view>
          <view class="modal-actions">
            <view class="btn btn-secondary" @tap="showCreate = false">取消</view>
            <view class="btn btn-primary" :class="{ disabled: creating }" @tap="doCreate">
              {{ creating ? '创建中...' : '创建' }}
            </view>
          </view>
        </view>
      </view>

      <!-- 加入弹窗 -->
      <view v-if="showJoin" class="mask" @tap.self="showJoin = false">
        <view class="modal">
          <view class="modal-title">🔑 输入邀请码</view>
          <view class="form-item">
            <view class="form-label">6 位邀请码</view>
            <input
              class="input invite-input"
              v-model="joinCode"
              placeholder="ABC123"
              maxlength="8"
              :value="joinCode"
              @input="onJoinCodeInput"
            />
          </view>
          <view class="modal-actions">
            <view class="btn btn-secondary" @tap="showJoin = false">取消</view>
            <view class="btn btn-primary" :class="{ disabled: joining }" @tap="doJoin">
              {{ joining ? '加入中...' : '加入' }}
            </view>
          </view>
        </view>
      </view>
    </block>

    <!-- 有家庭了 -->
    <block v-else>
      <view class="card family-card">
        <view class="fc-title">🏡 你已在家庭中</view>
        <view class="fc-name">{{ family.name }}</view>
        <view class="fc-code-row">
          <text class="fc-code-label">邀请码</text>
          <view class="fc-code">{{ family.invite_code }}</view>
          <view class="fc-copy" @tap="copyCode">复制</view>
        </view>
        <view class="fc-members">
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
            </view>
          </view>
        </view>
      </view>

      <view class="btn btn-danger btn-block" @tap="doLeave">退出家庭</view>
    </block>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import Taro from "@tarojs/taro";
import { createFamily, joinFamily, leaveFamily, getMyFamily } from "@/api/family";
import type { Family } from "@/types";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const { setFamily, refreshFamily } = userStore;

const defaultAvatar = "https://img.icons8.com/color/96/user-male-circle--v1.png";

const family = ref<Family | null>(null);
const showCreate = ref(false);
const showJoin = ref(false);
const createName = ref("");
const joinCode = ref("");
const creating = ref(false);
const joining = ref(false);

function onJoinCodeInput(e: any) {
  joinCode.value = (e.detail.value || "").toUpperCase();
}

async function load() {
  try {
    const res = await getMyFamily();
    family.value = res.data || null;
    setFamily(family.value);
  } catch {}
}

async function doCreate() {
  if (!createName.value.trim()) {
    Taro.showToast({ title: "请输入家庭名", icon: "none" });
    return;
  }
  creating.value = true;
  try {
    const res = await createFamily(createName.value.trim());
    family.value = res.data;
    setFamily(res.data);
    showCreate.value = false;
    createName.value = "";
    Taro.showToast({ title: "🎉 创建成功！", icon: "none" });
  } catch {} finally {
    creating.value = false;
  }
}

async function doJoin() {
  if (!joinCode.value.trim()) {
    Taro.showToast({ title: "请输入邀请码", icon: "none" });
    return;
  }
  joining.value = true;
  try {
    const res = await joinFamily(joinCode.value.trim().toUpperCase());
    family.value = res.data;
    setFamily(res.data);
    showJoin.value = false;
    joinCode.value = "";
    Taro.showToast({ title: "🎉 加入成功！", icon: "none" });
  } catch {} finally {
    joining.value = false;
  }
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

async function copyCode() {
  if (!family.value) return;
  await Taro.setClipboardData({ data: family.value.invite_code });
  Taro.showToast({ title: "已复制，发给另一半吧~", icon: "none" });
}

onMounted(load);
</script>

<style lang="scss" scoped>
@import '@/app.scss';

.page { padding-bottom: 40px; }

/* ===== Hero ===== */
.hero {
  background: $bg-gradient;
  padding: 50px 40px 40px;
  text-align: center;
  border-bottom-left-radius: 32px;
  border-bottom-right-radius: 32px;
  box-shadow: 0 8px 32px rgba(255, 45, 45, 0.2);
}
.hero-title { font-size: 48px; font-weight: 800; color: #fff; }
.hero-sub { font-size: 26px; color: rgba(255, 255, 255, 0.95); margin-top: 8px; }

/* ===== 动作卡片 ===== */
.action-card {
  display: flex;
  align-items: center;
  gap: 24px;
  margin: 24px;
  padding: 32px 28px;
  background: #fff;
  border-radius: 20px;
  box-shadow: $card-shadow;

  &:active { transform: scale(0.98); }
}
.action-icon {
  width: 100px; height: 100px;
  border-radius: 20px;
  background: linear-gradient(135deg, #FFF0E6, #FFE4CC);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56px;
}
.action-body { flex: 1; }
.action-title { font-size: 32px; font-weight: 700; color: #222; }
.action-sub { font-size: 24px; color: #999; margin-top: 6px; }
.action-arrow { font-size: 48px; color: #ccc; }

/* ===== 家庭卡 ===== */
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
  margin-bottom: 28px;
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
.fc-members-title { font-size: 26px; color: #666; margin-bottom: 16px; }
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

/* ===== Modal ===== */
.mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal {
  width: 600px;
  background: #fff;
  border-radius: 24px;
  padding: 32px;
}
.modal-title { font-size: 34px; font-weight: 700; color: #222; margin-bottom: 20px; }
.invite-input { letter-spacing: 6px; text-align: center; font-size: 36px; font-family: "Menlo", monospace; }
.modal-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}
.modal-actions .btn { flex: 1; }
.disabled { opacity: 0.5; }
</style>
