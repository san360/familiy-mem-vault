import { useState, useEffect, useCallback } from 'react'
import './App.css'
import MemoryForm from './components/MemoryForm'
import MemoryCard from './components/MemoryCard'
import FilterPanel from './components/FilterPanel'
import DeleteConfirmModal from './components/DeleteConfirmModal'
import api from './utils/api'

function App() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState('list') // 'list', 'add', 'edit'
  const [editingMemory, setEditingMemory] = useState(null)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({})
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [memoryToDelete, setMemoryToDelete] = useState(null)

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
      await api.createMemory(memoryData)
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
      setDeleteModalOpen(false)
      setMemoryToDelete(null)
      // Refresh memories with current filters to show updated results
      fetchMemories(filters)
    } catch (err) {
      console.error('Failed to delete memory:', err)
      setError('Failed to delete memory. Please try again.')
      setDeleteModalOpen(false)
      setMemoryToDelete(null)
    }
  }

  const confirmDelete = (memory) => {
    setMemoryToDelete(memory)
    setDeleteModalOpen(true)
  }

  const handleDeleteConfirm = () => {
    if (memoryToDelete) {
      handleDeleteMemory(memoryToDelete.id)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteModalOpen(false)
    setMemoryToDelete(null)
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
              <div className="mb-6 flex flex-col gap-4">
                {/* Search Bar */}
                <div className="max-w-2xl mx-auto w-full px-2 sm:px-0">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base sm:text-lg"
                      placeholder="Search your memories..."
                    />
                  </div>
                </div>

                {/* Action Bar */}
                <div className="flex flex-col sm:flex-row justify-between items-center gap-4 px-2 sm:px-0">
                  <button
                    onClick={() => setCurrentView('add')}
                    className="w-full sm:w-auto bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center justify-center space-x-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span>Add New Memory</span>
                  </button>
                  
                  <div className="text-sm text-gray-600">
                    {loading ? 'Loading...' : `${memories.filter(memory => 
                      memory.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                      memory.description.toLowerCase().includes(searchTerm.toLowerCase())
                    ).length} memories found`}
                  </div>
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
              ) : memories.filter(memory => 
                memory.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                memory.description.toLowerCase().includes(searchTerm.toLowerCase())
              ).length === 0 ? (
                <div className="text-center py-12">
                  <div className="max-w-md mx-auto">
                    <svg className="w-24 h-24 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-gray-500 text-lg mb-2">
                      {searchTerm ? 'No memories match your search' : 
                        (Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true)) 
                          ? 'No memories match your filters' 
                          : 'No memories yet!'
                        )
                      }
                    </p>
                    <p className="text-gray-400">
                      {searchTerm ? 'Try adjusting your search terms.' :
                        (Object.values(filters).some(f => f && (Array.isArray(f) ? f.length > 0 : true))
                          ? 'Try adjusting your filters to see more results.'
                          : 'Start by adding your first family memory.'
                        )
                      }
                    </p>
                  </div>
                </div>
              ) : (
                <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 px-2 sm:px-0">
                  {memories.filter(memory => 
                    memory.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    memory.description.toLowerCase().includes(searchTerm.toLowerCase())
                  ).map(memory => (
                    <MemoryCard
                      key={memory.id}
                      memory={memory}
                      onEdit={startEdit}
                      onDelete={confirmDelete}
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

        <DeleteConfirmModal
          isOpen={deleteModalOpen}
          memory={memoryToDelete}
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
        />
      </div>
    </div>
  )
}

export default App
