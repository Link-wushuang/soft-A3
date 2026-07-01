<template>
  <div class="home-page">
    <!-- 动态背景 -->
    <div class="bg-layer">
      <div class="bg-orb orb-1" /><div class="bg-orb orb-2" /><div class="bg-orb orb-3" />
      <div class="bg-grid" />
    </div>

    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-brand">
        <svg width="30" height="30" viewBox="0 0 28 28" fill="none">
          <rect width="28" height="28" rx="8" fill="url(#nav-grad)"/>
          <path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="1.6" fill="none"/>
          <circle cx="14" cy="14" r="3" fill="white" opacity="0.9"/>
          <defs><linearGradient id="nav-grad" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>
        </svg>
        <span class="brand-text">EduPath Agent</span>
      </div>
      <nav class="nav-links">
        <a href="#capabilities">核心能力</a>
        <a href="#loop">学习闭环</a>
        <a href="#resources">资源类型</a>
        <a href="#tech">技术架构</a>
      </nav>
      <div class="nav-cta">
        <button v-if="!isLoggedIn" class="btn-ghost" @click="$router.push('/login')">登录</button>
        <button class="btn-primary" @click="goToWorkspace">
          {{ isLoggedIn ? '进入工作台' : '立即体验' }}
          <span class="arrow">→</span>
        </button>
      </div>
    </header>

    <!-- Hero 区 -->
    <section class="hero">
      <div class="hero-badge">基于大模型的多智能体协同学习系统</div>
      <h1 class="hero-title">让每个人<br/>拥有专属学习路径</h1>
      <p class="hero-desc">
        EduPath Agent 通过对话式画像、个性化路径规划与多模态资源生成，
        构建「画像 → 规划 → 生成 → 练习 → 反思」的完整学习闭环，
        让每一份学习资源都为你而造。
      </p>
      <div class="hero-actions">
        <button class="btn-primary btn-lg" @click="goToWorkspace">
          {{ isLoggedIn ? '进入工作台' : '开始学习之旅' }}
          <span class="arrow">→</span>
        </button>
        <a v-if="!isLoggedIn" class="btn-ghost btn-lg" href="#loop">了解工作原理</a>
      </div>
      <div class="hero-stats">
        <div class="stat"><div class="stat-num">8</div><div class="stat-label">维学习画像</div></div>
        <div class="stat-divider" />
        <div class="stat"><div class="stat-num">14</div><div class="stat-label">协同智能体</div></div>
        <div class="stat-divider" />
        <div class="stat"><div class="stat-num">6</div><div class="stat-label">类学习资源</div></div>
        <div class="stat-divider" />
        <div class="stat"><div class="stat-num">5</div><div class="stat-label">阶段学习闭环</div></div>
      </div>
    </section>

    <!-- 核心能力 -->
    <section id="capabilities" class="section">
      <div class="section-head">
        <div class="section-tag">核心能力</div>
        <h2 class="section-title">四项能力，重构个性化学习</h2>
        <p class="section-sub">从理解学习者到生成专属资源，每一步都有智能体协同</p>
      </div>
      <div class="cap-grid">
        <div class="cap-card">
          <div class="cap-icon" style="background:linear-gradient(135deg,#6366f1,#818cf8)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 11C14.21 11 16 9.21 16 7S14.21 3 12 3 8 4.79 8 7 9.79 11 12 11ZM12 13C8.67 13 4 14.67 4 18V20H20V18C20 14.67 15.33 13 12 13Z" fill="white"/></svg>
          </div>
          <h3>对话式学习画像</h3>
          <p>通过自然对话提取 8 维学习特征：基础水平、学习目标、知识状态、薄弱点、已掌握、学习偏好、认知风格、时间预算，并基于证据动态更新。</p>
          <div class="cap-tags"><span>8 维度</span><span>证据化更新</span><span>动态追踪</span></div>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:linear-gradient(135deg,#8b5cf6,#a78bfa)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M3 6H21M3 12H21M3 18H21" stroke="white" stroke-width="2" stroke-linecap="round"/><circle cx="7" cy="6" r="2" fill="white"/><circle cx="15" cy="12" r="2" fill="white"/><circle cx="9" cy="18" r="2" fill="white"/></svg>
          </div>
          <h3>个性化路径规划</h3>
          <p>PathPlannerAgent 综合画像薄弱点、掌握情况与时间预算，生成有序学习路径，每个节点附带推荐理由。反思触发自动重规划。</p>
          <div class="cap-tags"><span>智能排序</span><span>动态重规划</span><span>理由可溯</span></div>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:linear-gradient(135deg,#ec4899,#f472b6)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="7" height="7" rx="1.5" fill="white"/><rect x="14" y="3" width="7" height="7" rx="1.5" fill="white" opacity="0.7"/><rect x="3" y="14" width="7" height="7" rx="1.5" fill="white" opacity="0.7"/><rect x="14" y="14" width="7" height="7" rx="1.5" fill="white"/></svg>
          </div>
          <h3>多智能体资源生成</h3>
          <p>6 类资源 Agent 并行生成讲解、思维导图、练习、案例、拓展阅读与视频分镜，经事实校验与安全过滤双重把关后呈现。</p>
          <div class="cap-tags"><span>并行生成</span><span>防幻觉校验</span><span>安全过滤</span></div>
        </div>
        <div class="cap-card">
          <div class="cap-icon" style="background:linear-gradient(135deg,#f59e0b,#fbbf24)">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M21 12C21 16.97 16.97 21 12 21S3 16.97 3 12 7.03 3 12 3C14.5 3 16.5 4 18 5.5" stroke="white" stroke-width="2" stroke-linecap="round"/><path d="M9 12L11 14L15 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <h3>练习反思闭环</h3>
          <p>评估答案 → 错因分析 → 画像反思更新 → 触发路径重规划，形成多智能体自主协同的学习改进闭环，让学习真正有效。</p>
          <div class="cap-tags"><span>自动评估</span><span>错因分析</span><span>闭环改进</span></div>
        </div>
      </div>
    </section>

    <!-- 学习闭环流程 -->
    <section id="loop" class="section section-tint">
      <div class="section-head">
        <div class="section-tag">学习闭环</div>
        <h2 class="section-title">五阶段闭环，让学习真正发生</h2>
        <p class="section-sub">多智能体协同驱动，每个阶段都为下一阶段提供结构化输入</p>
      </div>
      <div class="loop-flow">
        <div class="loop-step">
          <div class="loop-num">1</div>
          <div class="loop-body">
            <div class="loop-icon">💬</div>
            <div class="loop-title">对话建档</div>
            <div class="loop-agent">ProfileAgent</div>
            <div class="loop-desc">自然对话提取 8 维学习画像</div>
          </div>
        </div>
        <div class="loop-arrow">→</div>
        <div class="loop-step">
          <div class="loop-num">2</div>
          <div class="loop-body">
            <div class="loop-icon">🗺️</div>
            <div class="loop-title">路径规划</div>
            <div class="loop-agent">PathPlannerAgent</div>
            <div class="loop-desc">基于画像生成有序学习路径</div>
          </div>
        </div>
        <div class="loop-arrow">→</div>
        <div class="loop-step">
          <div class="loop-num">3</div>
          <div class="loop-body">
            <div class="loop-icon">⚡</div>
            <div class="loop-title">资源生成</div>
            <div class="loop-agent">6 Resource Agents 并行</div>
            <div class="loop-desc">并行生成 6 类个性化资源</div>
          </div>
        </div>
        <div class="loop-arrow">→</div>
        <div class="loop-step">
          <div class="loop-num">4</div>
          <div class="loop-body">
            <div class="loop-icon">✏️</div>
            <div class="loop-title">练习评估</div>
            <div class="loop-agent">EvaluationAgent</div>
            <div class="loop-desc">评分、错因分析与即时反馈</div>
          </div>
        </div>
        <div class="loop-arrow">→</div>
        <div class="loop-step">
          <div class="loop-num">5</div>
          <div class="loop-body loop-step-back">
            <div class="loop-icon">🔄</div>
            <div class="loop-title">反思重规划</div>
            <div class="loop-agent">ReflectionAgent → PathPlanner</div>
            <div class="loop-desc">画像更新触发路径自动重规划</div>
          </div>
        </div>
      </div>
      <div class="loop-back-hint">
        <span class="back-icon">↺</span>
        <span>反思阶段画像薄弱点变化时，自动回到第 2 阶段重新规划路径，形成持续改进闭环</span>
      </div>
    </section>

    <!-- 资源类型 -->
    <section id="resources" class="section">
      <div class="section-head">
        <div class="section-tag">资源类型</div>
        <h2 class="section-title">六类学习资源，覆盖多模态学习</h2>
        <p class="section-sub">每个知识点由 6 个专职 Agent 并行生成，匹配不同认知风格</p>
      </div>
      <div class="res-grid">
        <div class="res-card"><div class="res-emoji">📖</div><div class="res-name">个性化讲解</div><div class="res-agent">LectureAgent</div><p>Markdown 讲义，按画像调整深度与侧重</p></div>
        <div class="res-card"><div class="res-emoji">🧠</div><div class="res-name">思维导图</div><div class="res-agent">MindMapAgent</div><p>Mermaid 知识结构图，全局视角理解</p></div>
        <div class="res-card"><div class="res-emoji">✏️</div><div class="res-name">分层练习</div><div class="res-agent">ExerciseAgent</div><p>分难度练习题，含答案与解析</p></div>
        <div class="res-card"><div class="res-emoji">💻</div><div class="res-name">实操案例</div><div class="res-agent">CaseAgent</div><p>真实场景任务与参考实现</p></div>
        <div class="res-card"><div class="res-emoji">📚</div><div class="res-name">拓展阅读</div><div class="res-agent">ExtendedReadingAgent</div><p>精选阅读清单与内容摘要</p></div>
        <div class="res-card"><div class="res-emoji">🎬</div><div class="res-name">视频分镜</div><div class="res-agent">VideoStoryboardAgent</div><p>场景脚本与分镜脚本，多模态呈现</p></div>
      </div>
    </section>

    <!-- 技术架构 -->
    <section id="tech" class="section section-dark">
      <div class="section-head section-head-light">
        <div class="section-tag section-tag-light">技术架构</div>
        <h2 class="section-title section-title-light">多智能体协同，过程可追踪、内容可验证</h2>
        <p class="section-sub section-sub-light">中心化编排 + 角色分工，每个智能体的执行轨迹全程可视</p>
      </div>
      <div class="tech-grid">
        <div class="tech-card">
          <div class="tech-head"><span class="tech-dot" style="background:#6366f1" />中心化编排框架</div>
          <p>Orchestrator 作为中心调度器，按学习闭环阶段调用专职 Agent，资源生成与验证阶段采用线程池并行执行，显著降低端到端延迟。</p>
        </div>
        <div class="tech-card">
          <div class="tech-head"><span class="tech-dot" style="background:#8b5cf6" />防幻觉双重校验</div>
          <p>VerifierAgent 检查生成内容与知识库的事实一致性，ContentGuardAgent 进行安全与边界过滤，双重把关保障内容质量。</p>
        </div>
        <div class="tech-card">
          <div class="tech-head"><span class="tech-dot" style="background:#ec4899" />SSE 实时轨迹推送</div>
          <p>每个智能体的启动、耗时、状态、置信度通过 SSE 实时推送前端，避免黑盒生成，过程完全透明可追踪。</p>
        </div>
        <div class="tech-card">
          <div class="tech-head"><span class="tech-dot" style="background:#f59e0b" />反思驱动自协同</div>
          <p>ReflectionAgent 与 PathPlannerAgent 之间存在自主触发链，画像薄弱点变化主动触发路径重规划，实现 Agent 间协同闭环。</p>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="cta-card">
        <h2 class="cta-title">准备好开启你的专属学习之旅了吗？</h2>
        <p class="cta-desc">注册即可体验完整的多智能体个性化学习闭环</p>
        <button class="btn-primary btn-lg" @click="goToWorkspace">
          {{ isLoggedIn ? '进入工作台' : '立即开始' }}
          <span class="arrow">→</span>
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="home-footer">
      <div class="footer-brand">
        <span class="footer-name">EduPath Agent</span>
        <span class="footer-dot">·</span>
        <span>多智能体个性化学习资源生成系统</span>
      </div>
      <div class="footer-meta">
        <span>Powered by Multi-Agent System &amp; LLM</span>
        <span class="footer-dot">·</span>
        <span>软件杯 A3 赛题</span>
        <span class="footer-dot">·</span>
        <span>操作系统课程知识库</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function goToWorkspace() {
  if (isLoggedIn.value) {
    router.push('/student/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.home-page { position: relative; min-height: 100vh; background: #0f172a; color: #f1f5f9; overflow-x: hidden; }

/* 背景层 */
.bg-layer { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.bg-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 60px 60px; mask-image: radial-gradient(ellipse 80% 60% at 50% 30%, black 30%, transparent 75%); }
.bg-orb { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.14; animation: orbFloat 22s ease-in-out infinite; }
.orb-1 { width: 520px; height: 520px; background: #4f46e5; top: -18%; right: -8%; }
.orb-2 { width: 420px; height: 420px; background: #8b5cf6; bottom: -10%; left: -6%; animation-delay: -7s; }
.orb-3 { width: 320px; height: 320px; background: #ec4899; top: 45%; left: 42%; animation-delay: -13s; }
@keyframes orbFloat { 0%,100% { transform: translate(0,0) scale(1); } 25% { transform: translate(30px,-20px) scale(1.05); } 50% { transform: translate(-15px,25px) scale(0.95); } 75% { transform: translate(-25px,-10px) scale(1.02); } }

/* 通用容器 */
.top-nav, .hero, .section, .cta-section, .home-footer { position: relative; z-index: 1; }

/* 顶部导航 */
.top-nav { display: flex; align-items: center; justify-content: space-between; padding: 22px 56px; max-width: 1200px; margin: 0 auto; }
.nav-brand { display: flex; align-items: center; gap: 11px; }
.nav-brand .brand-text { font-size: 18px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.01em; }
.nav-links { display: flex; gap: 32px; }
.nav-links a { font-size: 13px; color: #94a3b8; text-decoration: none; transition: color var(--ep-transition); font-weight: 500; }
.nav-links a:hover { color: #e2e8f0; }
.nav-cta { display: flex; align-items: center; gap: 12px; }

/* 按钮 */
.btn-ghost { padding: 10px 20px; border-radius: 10px; font-size: 13px; font-weight: 600; color: #cbd5e1; background: transparent; border: 1px solid rgba(255,255,255,0.12); cursor: pointer; transition: all var(--ep-transition); text-decoration: none; display: inline-flex; align-items: center; }
.btn-ghost:hover { color: #f1f5f9; border-color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.05); }
.btn-primary { padding: 10px 22px; border-radius: 10px; font-size: 13px; font-weight: 600; color: white; background: linear-gradient(135deg, #4f46e5, #6366f1); border: none; cursor: pointer; transition: all var(--ep-transition); display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px rgba(79,70,229,0.35); }
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(79,70,229,0.5); }
.btn-primary .arrow { transition: transform var(--ep-transition); }
.btn-primary:hover .arrow { transform: translateX(3px); }
.btn-lg { padding: 14px 28px; font-size: 14px; }

/* Hero */
.hero { text-align: center; padding: 80px 32px 100px; max-width: 820px; margin: 0 auto; }
.hero-badge { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; color: #a5b4fc; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); margin-bottom: 32px; }
.hero-title { font-size: 52px; font-weight: 800; color: #f8fafc; margin: 0 0 24px; letter-spacing: -0.03em; line-height: 1.15; }
.hero-desc { font-size: 16px; color: #94a3b8; line-height: 1.8; margin: 0 auto 40px; max-width: 620px; }
.hero-actions { display: flex; gap: 16px; justify-content: center; margin-bottom: 64px; }
.hero-stats { display: flex; align-items: center; justify-content: center; gap: 28px; padding: 24px 40px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; backdrop-filter: blur(10px); }
.stat { text-align: center; }
.stat-num { font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #818cf8, #c084fc); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; line-height: 1; }
.stat-label { font-size: 12px; color: #94a3b8; margin-top: 6px; font-weight: 500; }
.stat-divider { width: 1px; height: 36px; background: rgba(255,255,255,0.1); }

/* 通用 section */
.section { padding: 90px 56px; max-width: 1200px; margin: 0 auto; }
.section-tint { max-width: none; background: rgba(255,255,255,0.02); border-top: 1px solid rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.06); }
.section-dark { background: linear-gradient(180deg, rgba(15,23,42,0.4), rgba(30,27,75,0.3)); border-top: 1px solid rgba(255,255,255,0.06); }
.section-head { text-align: center; margin-bottom: 56px; }
.section-tag { display: inline-block; padding: 4px 14px; border-radius: 16px; font-size: 11px; font-weight: 600; color: #a5b4fc; background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.25); margin-bottom: 18px; letter-spacing: 0.04em; }
.section-title { font-size: 34px; font-weight: 700; color: #f1f5f9; margin: 0 0 14px; letter-spacing: -0.02em; }
.section-sub { font-size: 15px; color: #94a3b8; margin: 0; }

/* 核心能力卡片 */
.cap-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.cap-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 28px 24px; transition: all var(--ep-transition-smooth); }
.cap-card:hover { background: rgba(255,255,255,0.06); border-color: rgba(99,102,241,0.3); transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.3); }
.cap-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px; box-shadow: 0 4px 14px rgba(0,0,0,0.2); }
.cap-card h3 { font-size: 17px; font-weight: 600; color: #f1f5f9; margin: 0 0 10px; }
.cap-card p { font-size: 13px; color: #94a3b8; line-height: 1.7; margin: 0 0 16px; }
.cap-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.cap-tags span { font-size: 11px; padding: 3px 9px; border-radius: 12px; background: rgba(99,102,241,0.1); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.18); }

/* 学习闭环流程 */
.loop-flow { display: flex; align-items: stretch; justify-content: center; gap: 8px; margin-bottom: 28px; }
.loop-step { flex: 1; max-width: 200px; position: relative; }
.loop-num { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; z-index: 2; box-shadow: 0 2px 8px rgba(99,102,241,0.4); }
.loop-body { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 26px 18px 20px; text-align: center; height: 100%; transition: all var(--ep-transition); }
.loop-step-back .loop-body { border-color: rgba(236,72,153,0.3); background: rgba(236,72,153,0.06); }
.loop-body:hover { background: rgba(255,255,255,0.07); border-color: rgba(99,102,241,0.4); transform: translateY(-2px); }
.loop-icon { font-size: 28px; margin-bottom: 12px; }
.loop-title { font-size: 15px; font-weight: 600; color: #f1f5f9; margin-bottom: 6px; }
.loop-agent { font-size: 11px; color: #a5b4fc; margin-bottom: 10px; font-family: monospace; }
.loop-desc { font-size: 12px; color: #94a3b8; line-height: 1.5; }
.loop-arrow { display: flex; align-items: center; color: #475569; font-size: 20px; padding: 0 2px; }
.loop-back-hint { text-align: center; padding: 16px 24px; background: rgba(236,72,153,0.08); border: 1px solid rgba(236,72,153,0.2); border-radius: 12px; color: #f9a8d4; font-size: 13px; display: inline-flex; align-items: center; gap: 10px; margin: 0 auto; max-width: fit-content; }
.back-icon { font-size: 18px; }

/* 资源类型 */
.res-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.res-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 28px 26px; transition: all var(--ep-transition-smooth); }
.res-card:hover { background: rgba(255,255,255,0.07); border-color: rgba(139,92,246,0.3); transform: translateY(-3px); }
.res-emoji { font-size: 36px; margin-bottom: 14px; }
.res-name { font-size: 17px; font-weight: 600; color: #f1f5f9; margin-bottom: 4px; }
.res-agent { font-size: 11px; color: #c4b5fd; margin-bottom: 12px; font-family: monospace; }
.res-card p { font-size: 13px; color: #94a3b8; line-height: 1.6; margin: 0; }

/* 技术架构 */
.section-head-light .section-title-light, .section-title-light { color: #f1f5f9; }
.section-sub-light { color: #94a3b8; }
.section-tag-light { background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.3); }
.tech-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.tech-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 26px 28px; }
.tech-head { display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 600; color: #f1f5f9; margin-bottom: 12px; }
.tech-dot { width: 8px; height: 8px; border-radius: 50%; }
.tech-card p { font-size: 13px; color: #94a3b8; line-height: 1.7; margin: 0; }

/* CTA */
.cta-section { padding: 80px 32px 100px; text-align: center; }
.cta-card { max-width: 640px; margin: 0 auto; padding: 56px 48px; background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.12)); border: 1px solid rgba(99,102,241,0.25); border-radius: 24px; backdrop-filter: blur(10px); }
.cta-title { font-size: 28px; font-weight: 700; color: #f8fafc; margin: 0 0 12px; letter-spacing: -0.02em; }
.cta-desc { font-size: 14px; color: #94a3b8; margin: 0 0 28px; }

/* Footer */
.home-footer { padding: 36px 56px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; }
.footer-brand { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 14px; color: #cbd5e1; margin-bottom: 8px; }
.footer-name { font-weight: 600; }
.footer-dot { color: #475569; }
.footer-meta { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 12px; color: #64748b; }

/* 响应式 */
@media (max-width: 1024px) {
  .cap-grid { grid-template-columns: repeat(2, 1fr); }
  .res-grid { grid-template-columns: repeat(2, 1fr); }
  .tech-grid { grid-template-columns: 1fr; }
  .nav-links { display: none; }
}
@media (max-width: 768px) {
  .top-nav { padding: 18px 24px; }
  .hero { padding: 48px 24px 60px; }
  .hero-title { font-size: 36px; }
  .section { padding: 60px 24px; }
  .hero-stats { flex-wrap: wrap; gap: 18px; padding: 18px 22px; }
  .stat-divider { display: none; }
  .loop-flow { flex-direction: column; align-items: center; }
  .loop-arrow { transform: rotate(90deg); padding: 4px 0; }
  .cap-grid, .res-grid { grid-template-columns: 1fr; }
  .cta-card { padding: 36px 24px; }
  .footer-meta { flex-wrap: wrap; }
}
</style>
