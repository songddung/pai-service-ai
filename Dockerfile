# Multi-stage build for PAI-service-AI
FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies including Rust for sudachipy
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libsndfile1 \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install flash-attention, causal-conv1d, mamba-ssm (commented out wheels from requirements.txt)
# Uncomment and modify these if needed for your specific torch version
# RUN pip install --no-cache-dir https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.2.post1/flash_attn-2.7.2.post1+cu12torch2.6cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
# RUN pip install --no-cache-dir https://github.com/Dao-AILab/causal-conv1d/releases/download/v1.5.0.post8/causal_conv1d-1.5.0.post8+cu12torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
# RUN pip install --no-cache-dir https://github.com/state-spaces/mamba/releases/download/v2.2.4/mamba_ssm-2.2.4+cu12torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl

# Copy application code
COPY src/ /app/src/

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/')"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
