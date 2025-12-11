# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Office Politics APP (StatsDashPublic v1.0.0) - A full-stack statistics dashboard application built with FastAPI backend and React/TypeScript frontend, containerized with Docker.

## Development Commands

### Initial Setup
```bash
./install              # Sets up Python venv and installs all dependencies (supports macOS/Linux/Windows)
. ./activate.sh        # Activates Python virtual environment
cd www && npm install  # Install frontend dependencies
```

### Running the Application
```bash
./dev                  # Starts full dev environment (backend on :8000, frontend on :4999)
./prod                 # Runs production server (builds frontend, starts uvicorn with 8 workers on port 80)
```

### Testing
```bash
./test                 # Runs all tests (Python + JavaScript)
./test --py            # Python tests only
./test --js            # JavaScript tests only
pytest tests -n auto -v # Direct pytest with parallel execution
cd www && npm test     # Frontend tests only (Mocha)
```

### Code Quality
```bash
./lint                 # Full linting pipeline: ruff, isort, black, flake8, mypy
ruff check --fix src tests  # Fast Python linter with auto-fix
black src tests        # Code formatting
mypy src tests         # Type checking
```

### Frontend Development
```bash
cd www
npm run start          # Webpack dev server on port 4999
npm run build          # Production build to dist/
npm run build:analyze  # Build with bundle size analysis
```

### Docker
```bash
docker-compose up      # Run containerized app on port 80
docker-compose up --build  # Rebuild and run
```

## Architecture

### Full-Stack Structure

**Backend (FastAPI + Python 3.7+)**
- Entry point: `src/mediabiasscorer/app.py`
- FastAPI initialization: `init_app.py` (CORS middleware)
- Frontend server setup: `init_frontend_app.py` (static files, API proxies)
- Background worker: `background_tasks.py` (60s update loop with shared memory)
- Configuration: `settings.py` (data dir, logs, IS_TEST flag)

**Frontend (React + TypeScript + Webpack)**
- Entry point: `www/src/index.ts`
- HTML template: `www/src/index.html`
- App initialization: `www/src/app.ts`
- Components: `www/src/components/`
- Webpack configs: `www/webpack/` (common, dev, prod)

### Development vs Production Mode

**Development** (`run_dev.py`):
- Backend: `localhost:8000` (Uvicorn)
- Frontend: `localhost:4999` (Webpack Dev Server with hot reload)
- Environment: `NPM_SERVER=http://localhost:4999` enables proxying
- Concurrent processes: Uvicorn + npm dev server + background tasks

**Production** (`prod.py`):
- Frontend built to `www/dist/`
- Backend serves static files from `www/dist/`
- Single port: 80 (or 8000 locally)
- Uvicorn with 8 workers
- Background tasks run in separate thread

### API Endpoints

- `/api/health` - Health check endpoint (GET)
- `/api` - Auto-generated OpenAPI/Swagger documentation
- All endpoints use Pydantic models for input/output (type-safe JSON)

### Database Design

- **ORM**: SQLAlchemy 2.0.19
- **Target**: PostgreSQL on render.com
- **Structure**:
  - `models.py` - ORM models for PostgreSQL database
  - `db.py` - Database queries, returns Pydantic objects
  - API endpoints accept and return Pydantic objects only

### Background Tasks & Shared Memory

- Background worker runs continuously (60s update interval)
- Uses `shared-memory-dict==0.7.2` for inter-process communication
- Defined in `memory_cache.py` with `SharedMemoryData` Pydantic model
- Intended for periodic scraping, data collection, scheduled jobs
- Error handling: catches exceptions, logs warnings, continues running

### Logging

- Location: `data/logs/system.log`
- Rotating logs: 512KB per file, 20 backups, gzipped
- Format: `LEVEL TIMESTAMP FILENAME:LINE (FUNCTION) - MESSAGE`

## Tech Stack

**Backend:**
- FastAPI with Uvicorn ASGI server
- SQLAlchemy 2.0.19 (PostgreSQL ORM)
- FastAPI-cache2 (shared memory dict)
- httpx (async HTTP client for proxying)
- python-dotenv (environment config)

**Frontend:**
- React 17.0.2 + TypeScript 5.2.2
- Webpack 5 (bundler with dev server)
- SASS/SCSS styling
- Chart.js (data visualization)
- PostHog.js v1.93.6 (analytics)
- Sweet Alert 2, Swiper, Video.js, Day.js

**Development:**
- Testing: pytest (Python), mochapack/mocha (JavaScript)
- Linting: ruff, flake8, pylint
- Formatting: black, isort
- Type checking: mypy
- CI/CD: GitHub Actions (Ubuntu, macOS, Windows)

## Environment Variables

```bash
IS_TEST=1              # Enables test mode (dev/test endpoints)
NPM_SERVER=http://localhost:4999  # Dev mode frontend proxy target
NODE_OPTIONS=--max_old_space_size=256  # npm build memory limit
```

Load from `.env` file using `python-dotenv`.

## Docker Configuration

- Base image: `nikolaik/python-nodejs:python3.11-nodejs20-alpine`
- Multi-stage build:
  1. Install Python dependencies from `requirements.txt`
  2. Install project in editable mode
  3. Build frontend with npm
  4. Expose port 80
  5. Run `./prod` script
- Docker Compose: Single service on port 80

## Project Notes

- Originally forked from `zackees/template-docker-fastapi-site`
- Current status: Boilerplate phase with basic health check endpoint
- Database models not yet fully implemented (awaiting requirements)
- README contains outdated text from template (noted in file)
- PWA-ready with manifest.json and service worker support
- Multi-platform CI/CD testing (macOS, Linux, Windows)
