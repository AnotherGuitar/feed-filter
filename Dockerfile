# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
# Note: This installs only production dependencies by default
# For dev dependencies, uncomment the line below
RUN uv pip install -e .
# RUN uv pip install -e ".[dev]"

# Copy application code
COPY src/ ./src/

# Optional: Copy tests if running tests in container
# COPY tests/ ./tests/

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command (override in docker-compose.yml or at runtime)
CMD ["python", "-m", "feed_filter.main"]
