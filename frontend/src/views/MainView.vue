<template>
  <div class="main-view">
    <h1>Process Project</h1>
    <p>Project ID: {{ projectId }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
  projectId: String
})
</script>

<style scoped>
.main-view {
  padding: 2rem;
}
</style>
