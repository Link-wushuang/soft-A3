import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/home', name: 'Home', component: () => import('../views/HomeView.vue') },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/student/dashboard', name: 'Dashboard', component: () => import('../views/student/Dashboard.vue') },
  { path: '/student/profile-chat', name: 'ProfileChat', component: () => import('../views/student/ProfileChat.vue') },
  { path: '/student/learning-path', name: 'LearningPath', component: () => import('../views/student/LearningPath.vue') },
  { path: '/student/knowledge-map', name: 'KnowledgeMap', component: () => import('../views/student/FullKnowledgeMap.vue') },
  { path: '/student/knowledge-progress', name: 'KnowledgeProgress', component: () => import('../views/student/FullKnowledgeProgress.vue') },
  { path: '/student/learning-records', name: 'LearningRecords', component: () => import('../views/student/LearningRecords.vue') },
  { path: '/student/study-plan', name: 'StudyPlan', component: () => import('../views/student/StudyPlan.vue') },
  { path: '/student/recommendations', name: 'Recommendations', component: () => import('../views/student/Recommendations.vue') },
  { path: '/student/resources/:knowledgePointId', name: 'ResourceGenerate', component: () => import('../views/student/ResourceGenerate.vue') },
  { path: '/student/exercise/:knowledgePointId', name: 'Exercise', component: () => import('../views/student/Exercise.vue') },
  { path: '/student/tutor/:knowledgePointId', name: 'TutorChat', component: () => import('../views/student/TutorChat.vue') },
  { path: '/student/tutor', name: 'GeneralTutor', component: () => import('../views/student/GeneralTutor.vue') },
  { path: '/teacher/knowledge', name: 'TeacherKnowledge', component: () => import('../views/teacher/KnowledgeManage.vue') },
  { path: '/teacher/analytics', name: 'TeacherAnalytics', component: () => import('../views/teacher/Analytics.vue') },
  { path: '/', redirect: '/home' },
]

const router = createRouter({ history: createWebHistory(), routes })

// 仅 /home 与 /login 为公开页面，其余需登录
const PUBLIC_PATHS = ['/home', '/login']
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (!PUBLIC_PATHS.includes(to.path) && !token) next('/login')
  else next()
})

export default router
