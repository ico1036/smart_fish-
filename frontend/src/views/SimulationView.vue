<template>
  <div class="simulation-view">
    <div class="sim-header">
      <h1>Simulation</h1>
      <span class="status" :class="status">{{ status }}</span>
    </div>

    <div class="controls">
      <button class="btn btn-primary" @click="startSimulation" :disabled="status === 'running'">
        {{ status === 'running' ? 'Running...' : 'Start Simulation' }}
      </button>
    </div>

    <div class="feed">
      <h2>Activity Feed</h2>
      <div v-for="(action, i) in actions" :key="i" class="action-item">
        <div class="action-header">
          <span class="round">R{{ action.round }}</span>
          <span class="agent-name">{{ action.agent }}</span>
          <span class="platform-tag">{{ action.platform }}</span>
        </div>
        <p class="action-content">{{ action.message }}</p>
      </div>
      <p v-if="!actions.length" class="empty">No actions yet. Start the simulation to see agent activity.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSimulation } from '../api/simulation'

const route = useRoute()
const status = ref('created')
const actions = ref([])
let ws = null

onMounted(async () => {
  try {
    const res = await getSimulation(route.params.id)
    status.value = res.data.status
  } catch (e) { console.error(e) }
})

const startSimulation = () => {
  status.value = 'running'
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/simulation/${route.params.id}/stream`
  ws = new WebSocket(wsUrl)

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'agent_action') {
      actions.value.unshift(data)
    } else if (data.type === 'simulation_complete') {
      status.value = 'completed'
    } else if (data.type === 'round_start') {
      actions.value.unshift({ round: data.round, agent: 'System', platform: '', message: `--- Round ${data.round} ---` })
    }
  }

  ws.onclose = () => { if (status.value === 'running') status.value = 'stopped' }
  ws.onerror = () => { status.value = 'error' }
}

onUnmounted(() => { if (ws) ws.close() })
</script>

<style scoped>
.simulation-view { max-width: 900px; margin: 0 auto; }
.sim-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.controls { margin-bottom: 2rem; }
.feed { background: #1a1d27; border-radius: 12px; padding: 1.5rem; }
.action-item { background: #252830; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; }
.action-header { display: flex; gap: 0.75rem; align-items: center; margin-bottom: 0.5rem; }
.round { background: #1565c0; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
.agent-name { font-weight: bold; color: #4fc3f7; }
.platform-tag { background: #3a3d4a; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }
.action-content { color: #bdbdbd; }
.empty { color: #616161; text-align: center; padding: 2rem; }
.status { font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 4px; background: #3a3d4a; }
.status.running { background: #e65100; }
.status.completed { background: #2e7d32; }
.btn { padding: 0.75rem 2rem; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; }
.btn-primary { background: #4fc3f7; color: #0f1117; font-weight: bold; }
</style>
