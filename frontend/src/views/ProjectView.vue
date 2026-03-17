<template>
  <div class="project-view" v-if="project">
    <div class="project-header">
      <h1>{{ project.name }}</h1>
      <span class="status" :class="project.status">{{ project.status }}</span>
    </div>

    <div class="section">
      <h2>Files</h2>
      <div v-for="f in project.files" :key="f.filename" class="file-item">
        {{ f.filename }} ({{ (f.size / 1024).toFixed(1) }}KB)
      </div>
    </div>

    <div class="section" v-if="project.ontology">
      <h2>Ontology</h2>
      <p>{{ project.ontology.analysis_summary }}</p>
      <div class="entity-types">
        <span v-for="et in project.ontology.entity_types" :key="et.name" class="tag">{{ et.name }}</span>
      </div>
    </div>

    <div class="actions">
      <button class="btn btn-primary" @click="buildGraph" :disabled="building">
        {{ building ? 'Building Graph...' : 'Build Knowledge Graph' }}
      </button>
      <button class="btn btn-secondary" @click="createSim" v-if="project.graph_id">
        Start Simulation
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject } from '../api/project'
import { buildGraph as apiBuildGraph } from '../api/graph'
import { createSimulation } from '../api/simulation'

const route = useRoute()
const router = useRouter()
const project = ref(null)
const building = ref(false)

onMounted(async () => {
  const res = await getProject(route.params.id)
  project.value = res.data
})

const buildGraph = async () => {
  building.value = true
  try {
    await apiBuildGraph({ project_id: route.params.id, simulation_requirement: '' })
  } catch (e) { console.error(e) }
  building.value = false
}

const createSim = async () => {
  const res = await createSimulation({
    project_id: route.params.id,
    graph_id: project.value.graph_id,
    platforms: ['twitter', 'reddit'],
    max_rounds: 10,
  })
  router.push(`/simulation/${res.data.simulation_id}`)
}
</script>

<style scoped>
.project-view { max-width: 900px; margin: 0 auto; }
.project-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.section { background: #1a1d27; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
.file-item { padding: 0.5rem; background: #252830; border-radius: 4px; margin-bottom: 0.5rem; }
.entity-types { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
.tag { background: #1565c0; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.85rem; }
.actions { display: flex; gap: 1rem; margin-top: 2rem; }
.status { font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 4px; background: #3a3d4a; }
.btn { padding: 0.75rem 2rem; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; }
.btn-primary { background: #4fc3f7; color: #0f1117; font-weight: bold; }
.btn-secondary { background: #3a3d4a; color: #e0e0e0; }
</style>
