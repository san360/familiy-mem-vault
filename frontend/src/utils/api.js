const API_BASE_URL = 'http://localhost:8000'

const api = {
  async getMemories() {
    const response = await fetch(`${API_BASE_URL}/api/memories`)
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