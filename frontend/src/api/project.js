import service from './index'

/**
 * List all projects
 */
export const listProjects = () => {
  return service.get('/api/project/list')
}

/**
 * Get project details
 */
export const getProject = (projectId) => {
  return service.get(`/api/project/${projectId}`)
}

/**
 * Upload project (files + metadata)
 */
export const uploadProject = (formData) => {
  return service({
    url: '/api/project/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * Delete project
 */
export const deleteProject = (projectId) => {
  return service.delete(`/api/project/${projectId}`)
}
