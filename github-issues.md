## 🧭 Sprint 1: Project Bootstrapping & Dev Environment

### 1. Initialize project with `azd` and deploy backend to Azure Container Apps (West Europe)
Use Azure Developer CLI (`azd`) to scaffold the FastAPI backend and deploy it to Azure Container Apps in the West Europe region.

**Acceptance Criteria:**
- FastAPI backend deployed with `azd up`
- App is reachable via public URL
- Resource group is created in West Europe

---

### 2. Set up full-stack project structure and development environment
Create the base folder structure:
- `/backend/` – FastAPI app, services, test suite
- `/frontend/` – React app using Vite + Tailwind CSS
- `/infra/` – Bicep or Terraform templates
- `/data/` – JSON memory storage (initial local DB)
- `.devcontainer/` – Codespaces-ready with Python/Node/Azure CLI
- `docker-compose.yml` – for local full-stack dev
- Shared `.env` config

**Acceptance Criteria:**
- Frontend and backend run locally with Docker
- DevContainer supports frontend and backend development

---

## 💡 Sprint 2: Core Functionality – Text Memories

### 3. Build responsive React UI for submitting and viewing memories
Use React + Tailwind to create:
- Memory form: Title, Date, Description, Tags, Location
- Create pages for adding, updating and deleting memory
- Grid/list to view memories
- Responsive mobile-friendly layout

**Test Cases:**
- Submit memory with all fields
- Display memories properly on mobile and desktop

---

### 4. Implement FastAPI backend endpoints for text memory management
Create RESTful API with the following routes:
- `POST /memories` – add new memory
- `GET /memories` – retrieve all memories
- `GET /memories/{id}` – fetch by ID
- `DELETE /memories/{id}` – delete memory
- Memory object includes: id, title, description, date, tags, location

**Test Cases:**
- Submit and retrieve memory
- Validate required fields
- JSON schema validation

---

### 5. Store memory data in local JSON file
Use a backend service in FastAPI to persist memory data in `data/memories.json`. Ensure:
- File-safe writing
- Unique ID generation
- Read, append, delete functions

**Test Cases:**
- Save and fetch multiple entries
- Handle empty or malformed file

---

### 6. Add filtering in UI and API: tag, location, date range
Update both frontend and backend to support:
- Tag-based filter (multiple tags)
- Location keyword filter
- Date range filter (`from`, `to`)

**Test Cases:**
- All filters apply correctly on API
- Frontend UI updates results dynamically

---

### 7. Add archive browsing by year and month
Add ability to group/browse memories by:
- Year → all memories from a given year
- Month → drill-down within year

**Test Cases:**
- Year/month filter returns valid results
- Memory grouping handled on backend

---

### 8. Write backend and frontend unit tests
Use:
- `pytest` for FastAPI
- `Jest` or `Vitest` for React

Test:
- API routes (GET, POST, DELETE)
- JSON storage logic
- UI form validation and filtering

**Test Cases:**
- Run `pytest` = all pass
- React form validation works as expected

---

## 🧠 Sprint 3: Image Upload & Generative AI

### 9. Enable image upload in React and backend
Frontend:
- Add image upload to memory form
Backend:
- Accept image upload via multipart/form-data
- Store in `/data/images/` locally
- Link to memory via `image_path`

**Test Cases:**
- Upload valid image
- Image shown in memory card
- Memory JSON includes image reference

---

### 10. Integrate Azure Blob Storage for image upload (Phase 2)
Replace local image storage with Blob Storage:
- Use Azure SDK for uploads
- Generate public or SAS-based URLs
- Save URL in memory object

**Acceptance Criteria:**
- Upload works from frontend
- URL displays image in memory card

---

### 11. Add AI-generated image caption using Azure OpenAI or Vision API
Backend:
- Call Azure AI to summarize uploaded image
Frontend:
- Display AI-generated caption in memory form as suggestion

**Test Cases:**
- Caption appears after upload
- Editable by user
- Fallback if image unreadable

---

### 12. Add search/filter by location for memories with images
Add a location-based search that shows only:
- Entries with a non-null `location` field
- And that have an image uploaded

**Test Cases:**
- Search by keyword in location
- Filter applies only to image-backed entries

---

## ☁️ Sprint 4: Deployment & Documentation

### 13. Create Dockerfile for backend and frontend apps
Write production Dockerfiles for:
- FastAPI backend (Python + Uvicorn)
- React frontend (Node + Nginx or Vite preview)
Use `docker-compose.yml` for dev orchestration

**Acceptance Criteria:**
- Both containers run locally
- Public ports correctly exposed

---

### 14. Deploy full stack with `azd` and infrastructure-as-code
Update `infra/` to include:
- Azure Container Apps (frontend + backend)
- Azure Storage (if needed)
- Environment configuration for both services

**Acceptance Criteria:**
- `azd up` deploys both containers
- Environment variables passed securely
- Public endpoint connects frontend to backend

---

### 15. Write complete README with usage, screenshots, and deploy guide
Document:
- App features and goals
- Screenshots or screencast link
- Local dev setup (Docker, VS Code)
- `azd` deployment instructions
- Optional AI config setup

---

## 🎁 Bonus Sprint: UX Polish & Showcase

### 16. Add advanced UI styling and transitions in React
Improve user experience:
- Memory cards with animations
- Responsive layout with Tailwind
- Optional dark/light theme

**Acceptance Criteria:**
- Mobile-friendly layout
- Smooth transitions between views

---

### 17. Record demo video and link in README
Create a short walkthrough video showing:
- Adding memory
- Browsing archive
- Uploading image + AI caption

**Acceptance Criteria:**
- Video hosted and linked in `README.md`
