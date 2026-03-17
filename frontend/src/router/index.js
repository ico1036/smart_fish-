import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue') },
  { path: '/project/:id', name: 'Project', component: () => import('../views/ProjectView.vue') },
  { path: '/graph/:id', name: 'Graph', component: () => import('../views/GraphView.vue') },
  { path: '/simulation/:id', name: 'Simulation', component: () => import('../views/SimulationView.vue') },
  { path: '/report/:id', name: 'Report', component: () => import('../views/ReportView.vue') },
  { path: '/chat/:reportId', name: 'Chat', component: () => import('../views/ChatView.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
