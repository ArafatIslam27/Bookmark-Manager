# Use the lightning-fast official uv python image
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Enable bytecode compilation for performance optimization
ENV UV_COMPILE_BYTECODE=1

# Copy your configuration and sync project dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY src/ ./src

# Expose port and start production ASGI server
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "--app-dir", "./src", "bookmark_manager.main:app", "--host", "0.0.0.0", "--port", "8000"]