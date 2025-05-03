FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy pyproject.toml
COPY pyproject.toml ./

# Configure Poetry to not use virtualenvs
RUN poetry config virtualenvs.create false

# Generate a fresh lock file and install dependencies
RUN poetry lock
ARG BUILD_ENV=prod
RUN if [ "$BUILD_ENV" = "dev" ] ; then poetry install --with dev && pip install pytest-asyncio ; else poetry install --no-dev ; fi

# Copy application code only (tests will be mounted at runtime)
COPY app/ ./app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the application port
EXPOSE 8000

# Default command runs the application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 