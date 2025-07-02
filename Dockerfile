# Dockerfile  –– copy the lines below verbatim
# ---- base image ----
FROM python:3.11-slim

# Disable .pyc files, force unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code last (leverages Docker layer cache)
COPY . .

# Cloud Run injects $PORT (defaults to 8080 locally)
ENV PORT=8080
EXPOSE 8080

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
