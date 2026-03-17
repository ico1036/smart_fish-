import api from './client'

export const generateReport = (data) => api.post('/report/generate', data)
export const getReportStatus = (taskId) => api.get(`/report/generate/status?task_id=${taskId}`)
export const getReport = (id) => api.get(`/report/${id}`)
export const chatWithReport = (reportId, data) => api.post(`/report/${reportId}/chat`, data)
