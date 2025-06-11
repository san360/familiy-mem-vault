const MemoryCard = ({ memory, onEdit, onDelete }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this memory?')) {
      onDelete(memory.id)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
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
              {memory.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={() => onEdit(memory)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="text-red-600 hover:text-red-800 text-sm font-medium transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}

export default MemoryCard