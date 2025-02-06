FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Create required directories
RUN mkdir sessions templates

# Copy application code last since it changes most frequently
COPY src/ .
COPY templates/ templates/

CMD ["python", "app.py"]
