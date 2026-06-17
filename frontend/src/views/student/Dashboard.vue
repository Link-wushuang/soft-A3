<template>
  <el-container style="padding:24px;max-width:1200px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center;height:auto;padding:16px 0">
      <h1 style="margin:0">学习仪表盘</h1>
      <el-button @click="$router.push('/student/profile-chat')">对话建档</el-button>
    </el-header>
    <el-main>
      <ProfileCard v-if="profile" :profile="profile" />
      <el-skeleton v-else :rows="4" animated />
      <el-card style="margin-top:16px">
        <template #header>快捷操作</template>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-button type="primary" style="width:100%" @click="$router.push('/student/learning-path')">查看学习路径</el-button>
          </el-col>
          <el-col :span="8">
            <el-button style="width:100%" @click="$router.push('/student/profile-chat')">更新学习画像</el-button>
          </el-col>
          <el-col :span="8">
            <el-button style="width:100%" @click="logout">退出登录</el-button>
          </el-col>
        </el-row>
      </el-card>
      <el-card v-if="profile?.weak_points?.length" style="margin-top:16px">
        <template #header>薄弱知识点</template>
        <el-tag v-for="tag in profile.weak_points" :key="tag" type="danger" style="margin:4px">{{ tag }}</el-tag>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import ProfileCard from '../../components/ProfileCard.vue'
import api from '../../api/index'

const router = useRouter()
const auth = useAuthStore()
const profile = ref<any>(null)

onMounted(async () => {
  try {
    const res = await api.get('/profile/1')
    profile.value = res.data
  } catch { /* no profile yet */ }
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
