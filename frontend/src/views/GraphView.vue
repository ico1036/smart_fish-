<template>
  <div class="graph-view">
    <h1>Knowledge Graph</h1>
    <div class="graph-container" ref="graphContainer"></div>
    <div class="stats" v-if="stats">
      <span>Nodes: {{ stats.node_count }}</span>
      <span>Edges: {{ stats.edge_count }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getGraphData } from '../api/graph'
import * as d3 from 'd3'

const route = useRoute()
const graphContainer = ref(null)
const stats = ref(null)

const renderGraph = (data) => {
  if (!graphContainer.value) return
  const container = graphContainer.value
  container.innerHTML = ''

  const width = container.clientWidth || 800
  const height = 600

  const svg = d3.select(container).append('svg').attr('width', width).attr('height', height)

  const simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.edges).id(d => d.node_id).distance(100))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))

  const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

  const link = svg.append('g').selectAll('line')
    .data(data.edges).enter().append('line')
    .attr('stroke', '#3a3d4a').attr('stroke-width', 1.5)

  const node = svg.append('g').selectAll('circle')
    .data(data.nodes).enter().append('circle')
    .attr('r', 8)
    .attr('fill', d => colorScale(d.labels?.[0] || 'default'))
    .call(d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended))

  const label = svg.append('g').selectAll('text')
    .data(data.nodes).enter().append('text')
    .text(d => d.name).attr('font-size', '10px').attr('fill', '#e0e0e0')
    .attr('dx', 12).attr('dy', 4)

  simulation.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    node.attr('cx', d => d.x).attr('cy', d => d.y)
    label.attr('x', d => d.x).attr('y', d => d.y)
  })

  function dragstarted(event, d) { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }
  function dragged(event, d) { d.fx = event.x; d.fy = event.y; }
  function dragended(event, d) { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }
}

onMounted(async () => {
  try {
    const res = await getGraphData(route.params.id)
    const data = res.data
    stats.value = { node_count: data.nodes.length, edge_count: data.edges.length }
    renderGraph({
      nodes: data.nodes.map(n => ({ ...n })),
      edges: data.edges.map(e => ({ source: e.source_id, target: e.target_id, ...e })),
    })
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.graph-view { max-width: 1200px; margin: 0 auto; }
.graph-container { background: #1a1d27; border-radius: 12px; min-height: 600px; overflow: hidden; }
.stats { display: flex; gap: 2rem; margin-top: 1rem; color: #9e9e9e; }
</style>
