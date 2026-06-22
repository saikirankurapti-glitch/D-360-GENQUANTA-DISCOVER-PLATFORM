# Dockerfile
# Multi-stage production build for Cheminformatics Service

# --- Stage 1: Build Dependencies ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies for compiling binary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies to user directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Runtime Runner ---
FROM python:3.11-slim as runner

WORKDIR /app

# Install system libraries required by RDKit drawing/rendering and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libxext6 \
    libglib2.0-0 \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Adjust PATH and python paths
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE 8004

# Run FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
