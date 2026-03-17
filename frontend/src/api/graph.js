import service, { requestWithRetry } from './index'

/**
 * Generate ontology (upload documents and simulation requirements)
 */
export function generateOntology(formData) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/ontology/generate',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  )
}

/**
 * Build graph
 */
export function buildGraph(data) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/build',
      method: 'post',
      data
    })
  )
}

/**
 * Get graph build status
 */
export function getBuildStatus(taskId) {
  return service({
    url: '/api/graph/build/status',
    method: 'get',
    params: { task_id: taskId }
  })
}

/**
 * Get task status
 */
export function getTaskStatus(taskId) {
  return service({
    url: `/api/graph/task/${taskId}`,
    method: 'get'
  })
}

/**
 * Get graph data
 * SmartFish endpoint: GET /api/graph/{id}
 */
export function getGraphData(graphId) {
  return service({
    url: `/api/graph/${graphId}`,
    method: 'get'
  })
}
