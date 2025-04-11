FROM python:3.10-slim

WORKDIR /app/src

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app/


ENV PYTHONPATH=/app/src

# Run the main script from inside src/
CMD ["python", "main.py"]
