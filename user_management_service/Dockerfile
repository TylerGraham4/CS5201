FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY user_management_service.py .

COPY templates /app/templates

EXPOSE 5001

CMD ["python", "user_management_service.py"]
