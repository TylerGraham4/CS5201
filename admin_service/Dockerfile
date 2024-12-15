FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY admin_service.py .

COPY templates /app/templates


EXPOSE 5003

CMD ["python", "admin_service.py"]
