import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return apiClient(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/auth/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    apiClient.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    apiClient.post('/auth/login', data),
  me: () => apiClient.get('/auth/me'),
  updateMe: (data: Partial<{ full_name: string; avatar_url: string }>) =>
    apiClient.patch('/auth/me', data),
}

// ─── Workspaces ───────────────────────────────────────────────────────────────
export const workspaceApi = {
  list: () => apiClient.get('/workspaces'),
  create: (data: { name: string; website?: string; industry?: string }) =>
    apiClient.post('/workspaces', data),
  get: (id: string) => apiClient.get(`/workspaces/${id}`),
  update: (id: string, data: object) => apiClient.patch(`/workspaces/${id}`, data),
}

// ─── Company / Analysis ───────────────────────────────────────────────────────
export const companyApi = {
  analyze: (workspaceId: string, url: string) =>
    apiClient.post(`/workspaces/${workspaceId}/analyze`, { website_url: url }),
  runPipeline: (workspaceId: string, url: string) =>
    apiClient.post(`/workspaces/${workspaceId}/pipeline/run`, { website_url: url }),
}

// ─── Leads ────────────────────────────────────────────────────────────────────
export const leadApi = {
  list: (workspaceId: string, params?: { page?: number; page_size?: number; status?: string }) =>
    apiClient.get(`/workspaces/${workspaceId}/leads`, { params }),
  get: (workspaceId: string, leadId: string) =>
    apiClient.get(`/workspaces/${workspaceId}/leads/${leadId}`),
  generate: (workspaceId: string, data: { company_id: string; count: number }) =>
    apiClient.post(`/workspaces/${workspaceId}/leads/generate`, data),
  update: (workspaceId: string, leadId: string, data: object) =>
    apiClient.patch(`/workspaces/${workspaceId}/leads/${leadId}`, data),
  delete: (workspaceId: string, leadId: string) =>
    apiClient.delete(`/workspaces/${workspaceId}/leads/${leadId}`),
}

// ─── Campaigns ────────────────────────────────────────────────────────────────
export const campaignApi = {
  list: (workspaceId: string) => apiClient.get(`/workspaces/${workspaceId}/campaigns`),
  create: (workspaceId: string, data: object) =>
    apiClient.post(`/workspaces/${workspaceId}/campaigns`, data),
  update: (workspaceId: string, id: string, data: object) =>
    apiClient.patch(`/workspaces/${workspaceId}/campaigns/${id}`, data),
  pause: (workspaceId: string, id: string) =>
    apiClient.post(`/workspaces/${workspaceId}/campaigns/${id}/pause`),
  resume: (workspaceId: string, id: string) =>
    apiClient.post(`/workspaces/${workspaceId}/campaigns/${id}/resume`),
  delete: (workspaceId: string, id: string) =>
    apiClient.delete(`/workspaces/${workspaceId}/campaigns/${id}`),
}

// ─── Emails ───────────────────────────────────────────────────────────────────
export const emailApi = {
  list: (workspaceId: string, params?: { page?: number; page_size?: number }) =>
    apiClient.get(`/workspaces/${workspaceId}/emails`, { params }),
  generate: (workspaceId: string, data: object) =>
    apiClient.post(`/workspaces/${workspaceId}/emails/generate`, data),
}

// ─── Analytics ────────────────────────────────────────────────────────────────
export const analyticsApi = {
  dashboard: (workspaceId: string) =>
    apiClient.get(`/workspaces/${workspaceId}/analytics/dashboard`),
  daily: (workspaceId: string, days?: number) =>
    apiClient.get(`/workspaces/${workspaceId}/analytics/daily`, { params: { days } }),
  campaigns: (workspaceId: string) =>
    apiClient.get(`/workspaces/${workspaceId}/analytics/campaigns`),
}

// ─── Agent Logs ───────────────────────────────────────────────────────────────
export const agentApi = {
  logs: (workspaceId: string) => apiClient.get(`/workspaces/${workspaceId}/agent-logs`),
}

// ─── Search ───────────────────────────────────────────────────────────────────
export const searchApi = {
  vector: (workspaceId: string, data: { query: string; collection: string; limit?: number }) =>
    apiClient.post(`/workspaces/${workspaceId}/search`, data),
}

// ─── Admin ────────────────────────────────────────────────────────────────────
export const adminApi = {
  stats: () => apiClient.get('/admin/stats'),
  users: () => apiClient.get('/admin/users'),
  deactivateUser: (id: string) => apiClient.patch(`/admin/users/${id}/deactivate`),
  activateUser: (id: string) => apiClient.patch(`/admin/users/${id}/activate`),
}
