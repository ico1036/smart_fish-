<template>
  <div class="home">
    <div class="header">
      <h1>SmartFish</h1>
      <p class="subtitle">Multi-Agent Swarm Intelligence Simulator</p>
    </div>

    <div class="upload-section">
      <h2>New Project</h2>
      <form @submit.prevent="handleUpload" class="upload-form">
        <input v-model="projectName" placeholder="Project name" class="input" />
        <textarea v-model="simRequirement" placeholder="Simulation requirement (what do you want to simulate?)" class="textarea" rows="3"></textarea>
        <div class="file-drop" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="handleDrop">
          <input ref="fileInput" type="file" multiple accept=".pdf,.md,.txt" @change="handleFiles" hidden />
          <p v-if="!files.length">Drop files here or click to upload (PDF, MD, TXT)</p>
          <p v-else>{{ files.length }} file(s) selected</p>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="!files.length || uploading">
          {{ uploading ? 'Uploading...' : 'Create Project' }}
        </button>
      </form>
    </div>

    <div class="projects-section" v-if="projects.length">
      <h2>Projects</h2>
      <div class="project-grid">
        <div v-for="p in projects" :key="p.project_id" class="project-card" @click="$router.push(`/project/${p.project_id}`)">
          <h3>{{ p.name }}</h3>
          <span class="status" :class="p.status">{{ p.status }}</span>
          <p class="meta">{{ p.files?.length || 0 }} files</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listProjects, uploadProject } from '../api/project'

const projects = ref([])
const projectName = ref('')
const simRequirement = ref('')
const files = ref([])
const uploading = ref(false)

onMounted(async () => {
  try {
    const res = await listProjects()
    projects.value = res.data
  } catch (e) { console.error(e) }
})

const handleFiles = (e) => { files.value = Array.from(e.target.files) }
const handleDrop = (e) => { files.value = Array.from(e.dataTransfer.files) }

const handleUpload = async () => {
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('project_name', projectName.value || 'Untitled')
    formData.append('simulation_requirement', simRequirement.value)
    files.value.forEach(f => formData.append('files', f))
    const res = await uploadProject(formData)
    projects.value.unshift(res.data)
    projectName.value = ''
    simRequirement.value = ''
    files.value = []
  } catch (e) { console.error(e) }
  uploading.value = false
}
</script>

<style scoped>
.home { max-width: 900px; margin: 0 auto; }
.header { text-align: center; margin-bottom: 3rem; }
.header h1 { font-size: 3rem; color: #4fc3f7; }
.subtitle { color: #9e9e9e; font-size: 1.2rem; margin-top: 0.5rem; }
.upload-section, .projects-section { background: #1a1d27; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; }
h2 { margin-bottom: 1rem; color: #e0e0e0; }
.input, .textarea { width: 100%; padding: 0.75rem; background: #252830; border: 1px solid #3a3d4a; border-radius: 8px; color: #e0e0e0; margin-bottom: 1rem; font-size: 1rem; }
.textarea { resize: vertical; }
.file-drop { border: 2px dashed #3a3d4a; border-radius: 8px; padding: 2rem; text-align: center; cursor: pointer; margin-bottom: 1rem; color: #9e9e9e; transition: border-color 0.2s; }
.file-drop:hover { border-color: #4fc3f7; }
.btn { padding: 0.75rem 2rem; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: all 0.2s; }
.btn-primary { background: #4fc3f7; color: #0f1117; font-weight: bold; }
.btn-primary:hover { background: #29b6f6; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.project-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }
.project-card { background: #252830; border-radius: 8px; padding: 1.5rem; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }
.project-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
.project-card h3 { margin-bottom: 0.5rem; }
.status { font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 4px; background: #3a3d4a; }
.status.graph_completed { background: #2e7d32; }
.status.created { background: #1565c0; }
.status.failed { background: #c62828; }
.meta { color: #9e9e9e; font-size: 0.85rem; margin-top: 0.5rem; }
</style>
