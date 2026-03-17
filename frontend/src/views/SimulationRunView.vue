<template>
  <div class="simulation-run-view">
    <h1>Simulation Run</h1>
    <p>Simulation ID: {{ simulationId }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
  simulationId: String
})
</script>

<style scoped>
.simulation-run-view {
  padding: 2rem;
}
</style>
