# Use Python 3.11 slim image based on stable Debian Bookworm
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \ 
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all AI application files
COPY . .

# Create plots directory for generated visualizations
RUN mkdir -p plots

# Expose port 8003 for the Flask application
EXPOSE 8003

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the chatbot visualizer
CMD ["python3", "chatbot_visualize.py"]
