import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Device API
export const deviceAPI = {
  getAll: (params) => api.get('/inventory/devices/', { params }),
  getById: (id) => api.get(`/inventory/devices/${id}`),
  create: (data) => api.post('/inventory/devices/', data),
  update: (id, data) => api.put(`/inventory/devices/${id}`, data),
  delete: (id) => api.delete(`/inventory/devices/${id}`),
};

// Temporary Signage API
export const temporarySignageAPI = {
  getAll: (params) => api.get('/inventory/temporary-signage/', { params }),
  getById: (id) => api.get(`/inventory/temporary-signage/${id}`),
  create: (data) => api.post('/inventory/temporary-signage/', data),
  update: (id, data) => api.put(`/inventory/temporary-signage/${id}`, data),
  delete: (id) => api.delete(`/inventory/temporary-signage/${id}`),
};

// Vertical Signage API
export const verticalSignageAPI = {
  getAll: (params) => api.get('/inventory/vertical-signage/', { params }),
  getById: (id) => api.get(`/inventory/vertical-signage/${id}`),
  create: (data) => api.post('/inventory/vertical-signage/', data),
  update: (id, data) => api.put(`/inventory/vertical-signage/${id}`, data),
  delete: (id) => api.delete(`/inventory/vertical-signage/${id}`),
};

// Stats API
export const statsAPI = {
  getStats: () => api.get('/inventory/stats/'),
  getLowStock: () => api.get('/inventory/low-stock/'),
};

export default api;