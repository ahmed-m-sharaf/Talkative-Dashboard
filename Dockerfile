# Use official slim Python 3.12 image for a small, secure build
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (curl for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Ensure the entrypoint script is executable
RUN chmod +x docker-entrypoint.sh

# Expose Streamlit (8501) and FastAPI (8005) ports
EXPOSE 8501 8005

# Define container healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Set the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
