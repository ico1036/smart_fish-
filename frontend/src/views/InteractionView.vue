<template>
  <div class="interaction-view">
    <h1>Interaction</h1>
    <p>Report ID: {{ reportId }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
  reportId: String
})
</script>

<style scoped>
.interaction-view {
  padding: 2rem;
}
</style>
