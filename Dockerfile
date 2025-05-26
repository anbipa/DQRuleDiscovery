FROM python:3.10-slim

WORKDIR /app

# Install build dependencies (if needed by any requirements)
#RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy source code and requirements
COPY requirements.txt .
COPY core ./core
COPY app ./app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so internal imports work
ENV PYTHONPATH="/app"

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "5000"]
