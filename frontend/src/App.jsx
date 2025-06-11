import { useState, useEffect } from 'react'
import './App.css'
import MemoryForm from './components/MemoryForm'
import MemoryCard from './components/MemoryCard'
import api from './utils/api'

function App() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentView, setCurrentView] = useState('list') // 'list', 'add', 'edit'
  const [editingMemory, setEditingMemory] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchMemories()
  }, [])

  const fetchMemories = async () => {
    try {
      setLoading(true)
      const data = await api.getMemories()
      setMemories(data.memories)
    } catch (err) {
      console.error('Failed to fetch memories:', err)
      setError('Failed to load memories. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAddMemory = async (memoryData) => {
    try {
      const newMemory = await api.createMemory(memoryData)
      setMemories(prev => [...prev, newMemory])
      setCurrentView('list')
      setError('')
    } catch {
      throw new Error('Failed to save memory. Please try again.')
    }
  }

  const handleEditMemory = async (memoryData) => {
    try {
      const updatedMemory = await api.updateMemory(editingMemory.id, memoryData)
      setMemories(prev => prev.map(memory => 
        memory.id === editingMemory.id ? updatedMemory : memory
      ))
      setCurrentView('list')
      setEditingMemory(null)
      setError('')
    } catch {
      throw new Error('Failed to update memory. Please try again.')
    }
  }

  const handleDeleteMemory = async (memoryId) => {
    try {
      await api.deleteMemory(memoryId)
      setMemories(prev => prev.filter(memory => memory.id !== memoryId))
      setError('')
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
              <div className="mb-6 text-center">
                <button
                  onClick={() => setCurrentView('add')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                  Add New Memory
                </button>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading memories...</p>
                </div>
              ) : memories.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg mb-4">No memories yet!</p>
                  <p className="text-gray-400">Start by adding your first family memory.</p>
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
