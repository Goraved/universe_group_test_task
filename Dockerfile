FROM python:3.12-slim

WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt

# Create empty directories for proper package structure
RUN mkdir -p api data config tests

# Copy the application code
COPY api/ ./api/
COPY data/ ./data/
COPY config/ ./config/
COPY tests/ ./tests/
COPY pytest.ini .

# Create proper Python package structure
RUN touch __init__.py api/__init__.py data/__init__.py config/__init__.py tests/__init__.py

# Set environment variables for API base URL
ENV API_BASE_URL=https://automation-qa-test.universeapps.limited

# Create directory for test reports
RUN mkdir -p reports

# Add the current directory to Python path to fix import issues
ENV PYTHONPATH=/app

# Create entrypoint script to check for API token
RUN echo '#!/bin/bash\n\
if [ -z "$API_TOKEN" ]; then\n\
  echo "ERROR: API_TOKEN environment variable is not set!"\n\
  echo "Please run with: docker run -e API_TOKEN=your_token ..."\n\
  exit 1\n\
fi\n\
\n\
pytest "$@"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to run all tests with HTML report
CMD ["--html=reports/report.html", "--self-contained-html", "tests/", "-n", "auto"]