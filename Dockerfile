# Stage 1: Frontend build
FROM node:18-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend
FROM python:3.11-slim AS backend
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project config and sync deps (cache layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy backend source
COPY backend/ ./backend/

# Install project
RUN uv sync --frozen --no-dev

# Copy frontend build
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Create data directories
RUN mkdir -p backend/data backend/uploads

EXPOSE 5001

CMD ["uv", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "5001"]
