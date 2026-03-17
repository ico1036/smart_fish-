<template>
  <div
    class="history-database"
    :class="{ 'no-projects': projects.length === 0 && !loading }"
  >
    <!-- Section Header -->
    <div class="section-header">
      <div class="section-line"></div>
      <span class="section-title">History</span>
      <div class="section-line"></div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <span>Loading projects...</span>
    </div>

    <!-- Project Cards -->
    <div v-else-if="projects.length > 0" class="cards-container">
      <div
        v-for="(project, index) in projects"
        :key="project.simulation_id || project.project_id || index"
        class="project-card"
        @click="navigateToProject(project)"
      >
        <div class="card-header">
          <span class="card-title">{{ project.project_name || project.name || 'Untitled' }}</span>
          <span class="card-status" :class="project.status">{{ project.status || 'unknown' }}</span>
        </div>
        <div class="card-meta">
          <span class="card-date">{{ formatDate(project.created_at) }}</span>
          <span class="card-files">{{ project.files_count || project.files?.length || 0 }} files</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No projects yet</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSimulationHistory } from '../api/simulation'

const router = useRouter()
const projects = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getSimulationHistory(20)
    if (res.success !== false) {
      projects.value = res.data || res || []
    }
  } catch (e) {
    console.warn('Failed to load history:', e)
  } finally {
    loading.value = false
  }
})

const navigateToProject = (project) => {
  if (project.simulation_id) {
    router.push({ name: 'Simulation', params: { id: project.simulation_id } })
  } else if (project.project_id) {
    router.push({ name: 'Project', params: { id: project.project_id } })
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  return d.toLocaleDateString()
}
</script>

<style scoped>
.history-database {
  padding: 60px 0;
  position: relative;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
}

.section-line {
  flex: 1;
  height: 1px;
  background: #E5E5E5;
}

.section-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: #999;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.loading-state,
.empty-state {
  text-align: center;
  color: #999;
  padding: 40px;
  font-size: 0.9rem;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.project-card {
  border: 1px solid #E5E5E5;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.project-card:hover {
  border-color: #999;
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.card-status {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  padding: 2px 8px;
  background: #F5F5F5;
  color: #666;
}

.card-status.graph_completed {
  background: #E8F5E9;
  color: #2E7D32;
}

.card-status.completed {
  background: #E8F5E9;
  color: #2E7D32;
}

.card-status.failed {
  background: #FFEBEE;
  color: #C62828;
}

.card-meta {
  display: flex;
  gap: 16px;
  font-size: 0.8rem;
  color: #999;
}
</style>
