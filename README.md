# Family Memory Vault

Family memory vault built with vibe coding...

## Project Structure

```
.
├── backend/              # FastAPI backend application
│   ├── main.py          # Main FastAPI app
│   ├── requirements.txt # Python dependencies
│   ├── Dockerfile       # Backend container config
│   └── tests/           # Backend test suite
├── frontend/            # React frontend application
│   ├── src/             # React source code
│   ├── package.json     # Node.js dependencies
│   ├── Dockerfile       # Frontend container config
│   └── Dockerfile.dev   # Development container config
├── infra/               # Azure infrastructure templates
│   ├── main.bicep       # Main Bicep template
│   └── core/            # Core infrastructure modules
├── data/                # JSON data storage
│   └── memories.json    # Sample memory data
├── .devcontainer/       # VS Code dev container config
├── docker-compose.yml   # Production container orchestration
├── docker-compose.dev.yml # Development container orchestration
├── azure.yaml           # Azure Developer CLI configuration
└── .env                 # Environment variables

```

## Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker
- Azure CLI (for deployment)

### Local Development

1. **Start with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

2. **Or run services individually:**
   
   **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testing

**Backend tests:**
```bash
cd backend
python -m pytest tests/ -v
```

**Frontend build:**
```bash
cd frontend
npm run build
```

## Azure Deployment

This project is configured for deployment with Azure Developer CLI (`azd`):

```bash
# Initialize (first time)
azd init

# Deploy to Azure
azd up
```

### Azure Resources

- **Container Apps Environment**: Hosts both frontend and backend
- **Container Registry**: Stores Docker images
- **Resource Group**: Contains all resources (deployed to West Europe)

## Features

- ✅ FastAPI backend with health checks
- ✅ React frontend with Tailwind CSS
- ✅ Docker containerization
- ✅ DevContainer support for Codespaces
- ✅ Azure Container Apps deployment ready
- ✅ JSON-based data storage
- ✅ Full-stack development environment

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/memories` - Get all family memories

## Environment Variables

- `PORT` - Backend server port (default: 8000)
- `VITE_API_BASE_URL` - Frontend API base URL
- `AZURE_LOCATION` - Azure deployment region (default: westeurope)
