<template>
  <div class="report-view" v-if="report">
    <h1>Analysis Report</h1>
    <div class="report-content" v-html="formatMarkdown(report.summary)"></div>
    <div class="sections" v-if="report.sections.length">
      <div v-for="s in report.sections" :key="s.order" class="section">
        <h2>{{ s.title }}</h2>
        <div v-html="formatMarkdown(s.content)"></div>
      </div>
    </div>
    <button class="btn btn-primary" @click="$router.push(`/chat/${route.params.id}`)">
      Chat with Report Agent
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReport } from '../api/report'

const route = useRoute()
const report = ref(null)

const formatMarkdown = (text) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

onMounted(async () => {
  try {
    const res = await getReport(route.params.id)
    report.value = res.data
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.report-view { max-width: 900px; margin: 0 auto; }
.report-content { background: #1a1d27; border-radius: 12px; padding: 2rem; margin: 1.5rem 0; line-height: 1.8; }
.section { background: #1a1d27; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }
.btn { padding: 0.75rem 2rem; border: none; border-radius: 8px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
.btn-primary { background: #4fc3f7; color: #0f1117; font-weight: bold; }
</style>
