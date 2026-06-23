import api from '../index'

export interface KPIData {
  value: number
  trend: number[]
  delta: number
  deltaLabel: string
  deltaDirection: 'up' | 'down' | 'flat'
}

export interface AttentionItem {
  type: 'inactive' | 'low_score' | 'improving'
  label: string
  value: number
  students: Array<{ id: number; name: string; avatar?: string; detail?: string }>
}

export interface DemoData {
  total_students: number
  total_answers: number
  overall_correctness_rate: number
  total_resources: number
  kpi: {
    students: KPIData
    answers: KPIData
    correctness: KPIData
    resources: KPIData
  }
  resource_type_counts: Record<string, number>
  top_mistake_tags: Array<{ tag: string; count: number }>
  correctness_rate_trend: Array<{ date: string; correctness_rate: number; total_answers: number }>
  weak_points_summary: string[]
}

export function getDemoData(): DemoData {
  const trend7 = [28, 35, 32, 40, 38, 45, 42]
  const trend7b = [120, 135, 128, 150, 145, 160, 155]
  const trend7c = [72, 68, 75, 70, 78, 74, 76]
  const trend7d = [8, 12, 10, 15, 13, 18, 16]

  return {
    total_students: 42,
    total_answers: 155,
    overall_correctness_rate: 76.8,
    total_resources: 16,
    kpi: {
      students: { value: 42, trend: [40, 40, 41, 41, 42, 42, 42], delta: 2, deltaLabel: '较上月+2人', deltaDirection: 'up' },
      answers: { value: 155, trend: trend7b, delta: 12.3, deltaLabel: '较上周+12.3%', deltaDirection: 'up' },
      correctness: { value: 76.8, trend: trend7c, delta: 1.2, deltaLabel: '较上周+1.2%', deltaDirection: 'up' },
      resources: { value: 16, trend: trend7d, delta: 0, deltaLabel: '与上周持平', deltaDirection: 'flat' },
    },
    resource_type_counts: {
      lecture: 5,
      mindmap: 3,
      exercise: 4,
      case: 2,
      extended_reading: 1,
      video_storyboard: 1,
    },
    top_mistake_tags: [
      { tag: '临界区与锁', count: 28 },
      { tag: '虚拟内存', count: 21 },
      { tag: '进程调度', count: 18 },
      { tag: '文件系统', count: 14 },
      { tag: '死锁检测', count: 10 },
      { tag: '系统调用', count: 7 },
      { tag: 'I/O 多路复用', count: 5 },
    ],
    correctness_rate_trend: [
      { date: '06-17', correctness_rate: 72.5, total_answers: 18 },
      { date: '06-18', correctness_rate: 68.0, total_answers: 22 },
      { date: '06-19', correctness_rate: 75.0, total_answers: 20 },
      { date: '06-20', correctness_rate: 70.2, total_answers: 25 },
      { date: '06-21', correctness_rate: 78.1, total_answers: 19 },
      { date: '06-22', correctness_rate: 74.3, total_answers: 23 },
      { date: '06-23', correctness_rate: 76.8, total_answers: 28 },
    ],
    weak_points_summary: [
      '临界区与锁',
      '虚拟内存',
      '进程调度',
      '文件系统实现',
      '死锁检测与恢复',
      '系统调用机制',
      'I/O 多路复用',
    ],
  }
}

export function getDemoAttention(): AttentionItem[] {
  return [
    {
      type: 'inactive',
      label: '一周未登录',
      value: 3,
      students: [
        { id: 1, name: '张三', detail: '7天未登录' },
        { id: 2, name: '李四', detail: '6天未登录' },
        { id: 3, name: '王五', detail: '5天未登录' },
      ],
    },
    {
      type: 'low_score',
      label: '连续3次低于60分',
      value: 5,
      students: [
        { id: 4, name: '赵六', detail: '近3次: 52, 48, 55' },
        { id: 5, name: '孙七', detail: '近3次: 58, 42, 50' },
        { id: 6, name: '周八', detail: '近3次: 45, 56, 51' },
        { id: 7, name: '吴九', detail: '近3次: 50, 53, 47' },
        { id: 8, name: '郑十', detail: '近3次: 55, 49, 52' },
      ],
    },
    {
      type: 'improving',
      label: '进步最快 Top 3',
      value: 3,
      students: [
        { id: 9, name: '陈一一', detail: '本周 +18%' },
        { id: 10, name: '林二三', detail: '本周 +15%' },
        { id: 11, name: '黄三四', detail: '本周 +12%' },
      ],
    },
  ]
}

export function getAttentionNeeded() {
  // Returns mock data; replace with real API when backend is ready
  return Promise.resolve({ data: getDemoAttention() })
}

export function fetchAnalytics(params?: { period?: string; start_date?: string; end_date?: string }) {
  return api.get('/analytics/teacher-summary', { params })
}
