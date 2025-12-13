FROM --platform=linux/amd64 python:3.11-slim

# Install Node.js 20 and basic tools
RUN apt-get update && apt-get install -y \
    curl \
    bash \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set environment
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Some packages failed, trying without cryptography..." && \
     pip install --no-cache-dir fastapi uvicorn[standard] pydantic python-dotenv SQLAlchemy httpx python-dateutil requests fastapi-cache2)

# Copy application code
COPY . .

# Install app as package
RUN pip install --no-cache-dir -e . || echo "Package install failed, continuing..."

# Build frontend
WORKDIR /app/www
RUN npm install --include=dev
RUN npm run build

# Back to app directory
WORKDIR /app

# The app will bind to PORT environment variable (provided by Render)
CMD ["/bin/bash", "prod"]
