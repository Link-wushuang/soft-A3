import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/student/dashboard', name: 'Dashboard', component: () => import('../views/student/Dashboard.vue') },
  { path: '/student/profile-chat', name: 'ProfileChat', component: () => import('../views/student/ProfileChat.vue') },
  { path: '/student/learning-path', name: 'LearningPath', component: () => import('../views/student/LearningPath.vue') },
  { path: '/student/resources/:knowledgePointId', name: 'ResourceGenerate', component: () => import('../views/student/ResourceGenerate.vue') },
  { path: '/student/exercise/:knowledgePointId', name: 'Exercise', component: () => import('../views/student/Exercise.vue') },
  { path: '/teacher/knowledge', name: 'TeacherKnowledge', component: () => import('../views/teacher/KnowledgeManage.vue') },
  { path: '/teacher/analytics', name: 'TeacherAnalytics', component: () => import('../views/teacher/Analytics.vue') },
  { path: '/', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
