FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
COPY ./src ./src
COPY ./api ./api

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so modules can be found
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Run API
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]