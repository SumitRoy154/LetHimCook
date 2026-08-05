# ==========================================
# 1. BUILD FRONTEND STAGE
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Install pnpm
RUN npm install -g pnpm

# Copy package files & install dependencies
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy frontend source code & build Next.js application
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

# ==========================================
# 2. PYTHON BACKEND STAGE
# ==========================================
FROM python:3.11-slim AS runner
WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements & install python packages
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source files & scripts
COPY backend/ /app/backend/
WORKDIR /app/backend

# Expose port (Railway passes PORT environment variable dynamically)
EXPOSE 8000

# Start script: seeds database staples & launches FastAPI with Uvicorn
CMD ["sh", "-c", "python scripts/migrate_and_seed_inventories.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
