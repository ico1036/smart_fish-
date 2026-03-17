import service, { requestWithRetry } from './index'

/**
 * Generate report
 */
export const generateReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/generate', data), 3, 1000)
}

/**
 * Get report generation status
 */
export const getReportStatus = (reportId) => {
  return service.get('/api/report/generate/status', { params: { report_id: reportId } })
}

/**
 * Get agent log (incremental)
 */
export const getAgentLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/agent-log`, { params: { from_line: fromLine } })
}

/**
 * Get console log (incremental)
 */
export const getConsoleLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/console-log`, { params: { from_line: fromLine } })
}

/**
 * Get report details
 */
export const getReport = (reportId) => {
  return service.get(`/api/report/${reportId}`)
}

/**
 * Chat with report agent
 */
export const chatWithReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/chat', data), 3, 1000)
}

/**
 * Interview report
 */
export const interviewReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/interview', data), 3, 1000)
}
