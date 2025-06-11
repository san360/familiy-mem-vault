import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch memories from backend API
    fetch('http://localhost:8000/api/memories')
      .then(res => res.json())
      .then(data => {
        setMemories(data.memories)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch memories:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Family Memory Vault
          </h1>
          <p className="text-lg text-gray-600">
            Preserve and share your precious family memories
          </p>
        </header>

        <main>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading memories...</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {memories.map(memory => (
                <div key={memory.id} className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {memory.title}
                  </h3>
                  <p className="text-gray-600 mb-4">{memory.description}</p>
                  <div className="text-sm text-gray-500">
                    Date: {memory.date}
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
