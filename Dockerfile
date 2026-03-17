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
RUN pip install uv

# Install backend dependencies
COPY backend/pyproject.toml ./backend/
RUN cd backend && uv sync --no-dev

# Copy backend source
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Create data directories
RUN mkdir -p backend/data backend/uploads

EXPOSE 5001

CMD ["uv", "run", "--directory", "backend", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]
