FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use virtualenvs inside Docker
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Copy the application code
COPY app/ ./app/

# Create a .env file at build time that can be overridden at runtime
RUN echo "OPENAI_API_KEY=your_api_key_here" > .env \
    && echo "OPENAI_MODEL=gpt-4o-2024-08-06" >> .env

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 