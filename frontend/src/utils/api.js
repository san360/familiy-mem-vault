// Use environment variable, or detect if we're in Codespace and use appropriate URL
const getApiBaseUrl = () => {
  // Check for explicit environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Check if we're in a Codespace by looking at the hostname
  if (typeof window !== 'undefined' && window.location.hostname.includes('app.github.dev')) {
    // Extract the Codespace name from current URL and use port 8000
    const hostname = window.location.hostname;
    const codespaceUrl = hostname.replace('-5173', '-8000').replace('-5175', '-8000');
    return `https://${codespaceUrl}`;
  }
  
  // Default to localhost for local development
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

const api = {
  async getMemories(filters = {}) {
    const params = new URLSearchParams()
    
    if (filters.tags && filters.tags.length > 0) {
      filters.tags.forEach(tag => params.append('tags', tag))
    }
    
    if (filters.location) {
      params.append('location', filters.location)
    }
    
    if (filters.date_from) {
      params.append('date_from', filters.date_from)
    }
    
    if (filters.date_to) {
      params.append('date_to', filters.date_to)
    }
    
    const queryString = params.toString()
    const url = `${API_BASE_URL}/api/memories${queryString ? `?${queryString}` : ''}`
    
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error('Failed to fetch memories')
    }
    return response.json()
  },

  async getMemory(id) {
    const response = await fetch(`${API_BASE_URL}/api/memories/${id}`)
    if (!response.ok) {
      throw new Error('Failed to fetch memory')
    }
    return response.json()
  },

  async createMemory(memoryData) {
    const response = await fetch(`${API_BASE_URL}/api/memories`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(memoryData),
    })
    if (!response.ok) {
      throw new Error('Failed to create memory')
    }
    return response.json()
  },

  async updateMemory(id, memoryData) {
    const response = await fetch(`${API_BASE_URL}/api/memories/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(memoryData),
    })
    if (!response.ok) {
      throw new Error('Failed to update memory')
    }
    return response.json()
  },

  async deleteMemory(id) {
    const response = await fetch(`${API_BASE_URL}/api/memories/${id}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error('Failed to delete memory')
    }
    return response.json()
  }
}

export default api