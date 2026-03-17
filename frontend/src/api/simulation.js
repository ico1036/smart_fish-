import api from './client'

export const createSimulation = (data) => api.post('/simulation/create', data)
export const getSimulation = (id) => api.get(`/simulation/${id}`)
