import { useState } from 'react'

const MemoryCard = ({ memory, onEdit, onDelete }) => {
  const [imageError, setImageError] = useState(false)
  
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const handleImageError = () => {
    setImageError(true)
  }

  const handleDelete = () => {
    onDelete(memory)
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      {/* Image Section */}
      {memory.imageUrl && !imageError ? (
        <div className="w-full h-48 overflow-hidden">
          <img
            src={memory.imageUrl}
            alt={memory.title}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
        </div>
      ) : (
        <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
          <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      )}
      
      {/* Clickable content area */}
      <div 
        className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => onEdit(memory)}
      >
        <div className="flex flex-col h-full">
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {memory.title}
            </h3>
            <p className="text-gray-600 mb-4 flex-1">
              {memory.description}
            </p>
          </div>
          
          <div className="space-y-2">
            <div className="text-sm text-gray-500">
              <span className="font-medium">Date:</span> {formatDate(memory.date)}
            </div>
            
            {memory.location && (
              <div className="text-sm text-gray-500">
                <span className="font-medium">Location:</span> {memory.location}
              </div>
            )}
            
            {memory.tags && memory.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {memory.tags.map((tag, index) => {
                  // Create colorful pills with different colors based on tag hash
                  const colors = [
                    'bg-blue-100 text-blue-800',
                    'bg-green-100 text-green-800',
                    'bg-purple-100 text-purple-800',
                    'bg-yellow-100 text-yellow-800',
                    'bg-pink-100 text-pink-800',
                    'bg-indigo-100 text-indigo-800',
                    'bg-red-100 text-red-800',
                    'bg-orange-100 text-orange-800'
                  ]
                  const colorIndex = tag.length % colors.length
                  
                  return (
                    <span
                      key={index}
                      className={`inline-block ${colors[colorIndex]} text-xs px-2 py-1 rounded-full font-medium`}
                    >
                      {tag}
                    </span>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Action buttons - not clickable for edit */}
      <div className="flex justify-end gap-2 px-6 pb-4 border-t border-gray-200">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onEdit(memory)
          }}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
        >
          Edit
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            handleDelete()
          }}
          className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  )
}

export default MemoryCard