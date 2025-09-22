FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r coboleval && useradd -r -g coboleval coboleval

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY *.md ./
COPY *.json ./

# Create results directory
RUN mkdir -p /results && chown -R coboleval:coboleval /app /results

# Switch to non-root user
USER coboleval

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "src/complete_cobol_evaluator.py"]