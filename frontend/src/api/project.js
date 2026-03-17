import api from './client'

export const listProjects = () => api.get('/project/list')
export const getProject = (id) => api.get(`/project/${id}`)
export const uploadProject = (formData) => api.post('/project/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const deleteProject = (id) => api.delete(`/project/${id}`)
