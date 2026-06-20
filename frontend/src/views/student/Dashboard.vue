<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">学习仪表盘</h1>
        <p class="page-subtitle">欢迎回来，{{ auth.user?.display_name || '同学' }}</p>
      </div>
      <el-button type="primary" @click="$router.push('/student/profile-chat')">
        <el-icon style="margin-right:6px"><ChatDotRound /></el-icon>
        对话建档
      </el-button>
    </div>

    <div v-if="profile" class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background:#eff6ff;color:#2563eb">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ levelLabels[profile.base_level] || profile.base_level }}</div>
          <div class="stat-label">基础水平</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fef2f2;color:#ef4444">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.weak_points?.length || 0 }}</div>
          <div class="stat-label">薄弱知识点</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#ecfdf5;color:#10b981">
          <el-icon><SuccessFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.mastered_points?.length || 0 }}</div>
          <div class="stat-label">已掌握知识点</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#f5f3ff;color:#7c3aed">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.time_budget || '—' }}</div>
          <div class="stat-label">时间预算</div>
        </div>
      </div>
    </div>
    <el-skeleton v-else :rows="2" animated style="margin-bottom:24px" />

    <div class="content-grid">
      <div class="content-main">
        <ProfileCard v-if="profile" :profile="profile" />

        <div class="card" style="margin-top:20px">
          <div class="card-header">快捷操作</div>
          <div class="card-body">
            <div class="action-grid">
              <button class="action-card" @click="$router.push('/student/learning-path')">
                <div class="action-icon" style="background:#eff6ff;color:#2563eb">
                  <el-icon :size="22"><Guide /></el-icon>
                </div>
                <div class="action-label">查看学习路径</div>
                <div class="action-desc">根据画像规划学习路线</div>
              </button>
              <button class="action-card" @click="$router.push('/student/profile-chat')">
                <div class="action-icon" style="background:#f5f3ff;color:#7c3aed">
                  <el-icon :size="22"><ChatDotRound /></el-icon>
                </div>
                <div class="action-label">更新学习画像</div>
                <div class="action-desc">通过对话完善个人画像</div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="content-aside">
        <div v-if="profile?.weak_points?.length" class="card">
          <div class="card-header" style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:#ef4444"><WarningFilled /></el-icon>
            薄弱知识点
          </div>
          <div class="card-body">
            <div class="tag-list">
              <el-tag v-for="tag in profile.weak_points" :key="tag" type="danger" effect="light" round>{{ tag }}</el-tag>
            </div>
          </div>
        </div>

        <div v-if="profile?.mastered_points?.length" class="card" style="margin-top:16px">
          <div class="card-header" style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:#10b981"><SuccessFilled /></el-icon>
            已掌握知识点
          </div>
          <div class="card-body">
            <div class="tag-list">
              <el-tag v-for="tag in profile.mastered_points" :key="tag" type="success" effect="light" round>{{ tag }}</el-tag>
            </div>
          </div>
        </div>

        <div v-if="profile?.learning_preference?.length" class="card" style="margin-top:16px">
          <div class="card-header">学习偏好</div>
          <div class="card-body">
            <div class="tag-list">
              <el-tag v-for="pref in profile.learning_preference" :key="pref" effect="light" round>{{ pref }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import ProfileCard from '../../components/ProfileCard.vue'
import { ChatDotRound, Guide, User, WarningFilled, SuccessFilled, Timer } from '@element-plus/icons-vue'
import api from '../../api/index'

const auth = useAuthStore()
const profile = ref<any>(null)

const levelLabels: Record<string, string> = {
  beginner: '初学者',
  medium: '中等',
  advanced: '进阶',
}

onMounted(async () => {
  try {
    const res = await api.get('/profile/1')
    profile.value = res.data
  } catch { /* no profile yet */ }
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  padding: 20px;
  border: 1px solid var(--ep-border-light);
  border-radius: var(--ep-radius-md);
  background: var(--ep-bg-hover);
  cursor: pointer;
  transition: all var(--ep-transition);
  text-align: left;
}

.action-card:hover {
  border-color: var(--ep-primary);
  background: var(--ep-primary-light);
  transform: translateY(-2px);
  box-shadow: var(--ep-shadow-sm);
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--ep-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-label {
  font-weight: 600;
  font-size: 14px;
  color: var(--ep-text-primary);
}

.action-desc {
  font-size: 12px;
  color: var(--ep-text-secondary);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
