FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy and install dependencies from the subdirectory
COPY cloud-threat-detection-platform/backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code from the subdirectory
COPY cloud-threat-detection-platform/backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
