import { useCallback, useEffect, useState } from 'react'
import DeleteConfirmModal from './components/DeleteConfirmModal'
import MemoryCard from './components/MemoryCard'
import MemoryForm from './components/MemoryForm'
import api from './utils/api'

function App() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState('list') // 'list', 'add', 'edit'
  const [editingMemory, setEditingMemory] = useState(null)
  const [error, setError] = useState('')
  const [filters] = useState({})
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
    <div className="min-h-screen bg-gradient-to-b from-purple-100 via-white to-blue-100 py-0 px-0 sm:py-4 sm:px-4 flex flex-col items-center">
      <div className="w-full max-w-md sm:max-w-3xl md:max-w-5xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-6 sm:py-8 bg-white bg-opacity-90 rounded-b-3xl shadow-lg mb-8">
          <div className="flex items-center gap-3">
            <div className="bg-purple-200 rounded-xl p-2">
              <svg className="w-10 h-10 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <rect x="4" y="4" width="16" height="16" rx="4" strokeWidth="2" />
                <circle cx="12" cy="12" r="3" strokeWidth="2" />
              </svg>
            </div>
            <div>
              <span className="block text-xl sm:text-2xl font-bold text-gray-900 leading-tight">Family</span>
              <span className="block text-lg sm:text-xl font-semibold text-gray-700 -mt-1">Memory Vault</span>
            </div>
          </div>
          <nav className="flex items-center gap-6">
            <span className="text-purple-700 font-semibold text-lg cursor-pointer border-b-2 border-purple-600 pb-1">Memories</span>
            <button
              onClick={() => setCurrentView('add')}
              className="text-gray-700 hover:text-purple-700 font-medium text-lg focus:outline-none"
            >
              Add Memory
            </button>
          </nav>
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
              {/* Search Bar */}
              <div className="mb-6 flex flex-col gap-4">
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
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-base sm:text-lg shadow-sm"
                      placeholder="Search..."
                    />
                  </div>
                </div>
              </div>

              {/* Memories Grid */}
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
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
                <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 px-2 sm:px-0">
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

              {/* Add Memory Button (fixed at bottom) */}
              <div className="fixed bottom-6 left-0 w-full flex justify-center z-50 pointer-events-none">
                <button
                  onClick={() => setCurrentView('add')}
                  className="pointer-events-auto bg-gradient-to-r from-purple-500 to-blue-400 hover:from-purple-600 hover:to-blue-500 text-white text-lg font-semibold px-10 py-4 rounded-full shadow-xl focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 transition-colors"
                >
                  Add Memory
                </button>
              </div>
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
