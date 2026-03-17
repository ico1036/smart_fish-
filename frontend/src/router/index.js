import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/HomeView.vue') },
  { path: '/process/:projectId', name: 'Process', component: () => import('../views/MainView.vue'), props: true },
  { path: '/simulation/:id', name: 'Simulation', component: () => import('../views/SimulationView.vue'), props: true },
  { path: '/simulation/:simulationId/start', name: 'SimulationRun', component: () => import('../views/SimulationRunView.vue'), props: true },
  { path: '/report/:reportId', name: 'Report', component: () => import('../views/ReportView.vue'), props: true },
  { path: '/interaction/:reportId', name: 'Interaction', component: () => import('../views/InteractionView.vue'), props: true },
]

export default createRouter({ history: createWebHistory(), routes })
