import api from './client'

export const buildGraph = (data) => api.post('/graph/build', data)
export const getBuildStatus = (taskId) => api.get(`/graph/build/status?task_id=${taskId}`)
export const getGraphData = (graphId) => api.get(`/graph/${graphId}`)
