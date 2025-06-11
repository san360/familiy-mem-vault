import { useState, useEffect, useCallback } from 'react'
import './App.css'
import MemoryForm from './components/MemoryForm'
import MemoryCard from './components/MemoryCard'
import FilterPanel from './components/FilterPanel'
import api from './utils/api'

function App() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState('list') // 'list', 'add', 'edit'
  const [editingMemory, setEditingMemory] = useState(null)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({})
  const [filtersOpen, setFiltersOpen] = useState(false)

  const fetchMemories = useCallback(async (appliedFilters = {}) => {
    try {
      setLoading(true)
      const data = await api.getMemories(appliedFilters)
      setMemories(data.memories)
    } catch (err) {
      console.error('Failed to fetch memories:', err)
      setError('Failed to load memories. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMemories()
  }, [fetchMemories])

  const handleFiltersChange = useCallback((newFilters) => {
    setFilters(newFilters)
    fetchMemories(newFilters)
  }, [fetchMemories])

  const handleAddMemory = async (memoryData) => {
    try {
      const newMemory = await api.createMemory(memoryData)
      setCurrentView('list')
      setError('')
      // Refresh memories with current filters to show updated results
      fetchMemories(filters)
    } catch {
      throw new Error('Failed to save memory. Please try again.')
    }
  }

  const handleEditMemory = async (memoryData) => {
    try {
      await api.updateMemory(editingMemory.id, memoryData)
      setCurrentView('list')
      setEditingMemory(null)
      setError('')
      // Refresh memories with current filters to show updated results
      fetchMemories(filters)
    } catch {
      throw new Error('Failed to update memory. Please try again.')
    }
  }

  const handleDeleteMemory = async (memoryId) => {
    try {
      await api.deleteMemory(memoryId)
      setError('')
      // Refresh memories with current filters to show updated results
      fetchMemories(filters)
    } catch (err) {
      console.error('Failed to delete memory:', err)
      setError('Failed to delete memory. Please try again.')
    }
  }

  const startEdit = (memory) => {
    setEditingMemory(memory)
    setCurrentView('edit')
  }

  const cancelForm = () => {
    setCurrentView('list')
    setEditingMemory(null)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 px-4 sm:py-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            Family Memory Vault
          </h1>
          <p className="text-base sm:text-lg text-gray-600">
            Preserve and share your precious family memories
          </p>
        </header>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md max-w-2xl mx-auto">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={() => setError('')}
              className="mt-2 text-sm text-red-800 underline hover:no-underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <main>
          {currentView === 'list' && (
            <>
              <div className="mb-6 flex flex-col sm:flex-row justify-between items-center gap-4">
                <button
                  onClick={() => setCurrentView('add')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Add New Memory</span>
                </button>
                
                <div className="text-sm text-gray-600">
                  {loading ? 'Loading...' : `${memories.length} memories found`}
                </div>
              </div>

              <FilterPanel 
                onFiltersChange={handleFiltersChange}
                isOpen={filtersOpen}
                onToggle={() => setFiltersOpen(!filtersOpen)}
              />

              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading memories...</p>
                </div>
              ) : memories.length === 0 ? (
                <div className="text-center py-12">
                  <div className="max-w-md mx-auto">
                    <svg className="w-24 h-24 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-gray-500 text-lg mb-2">
                      {Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true)) 
                        ? 'No memories match your filters' 
                        : 'No memories yet!'
                      }
                    </p>
                    <p className="text-gray-400">
                      {Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true))
                        ? 'Try adjusting your filters to see more results.'
                        : 'Start by adding your first family memory.'
                      }
                    </p>
                  </div>
                </div>
              ) : (
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {memories.map(memory => (
                    <MemoryCard
                      key={memory.id}
                      memory={memory}
                      onEdit={startEdit}
                      onDelete={handleDeleteMemory}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {currentView === 'add' && (
            <MemoryForm
              onSubmit={handleAddMemory}
              onCancel={cancelForm}
            />
          )}

          {currentView === 'edit' && editingMemory && (
            <MemoryForm
              memory={editingMemory}
              onSubmit={handleEditMemory}
              onCancel={cancelForm}
            />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
