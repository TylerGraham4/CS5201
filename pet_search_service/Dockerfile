FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pet_search_service.py .

# Copy templates and static files
COPY templates /app/templates
COPY static /app/static

# Expose the port the app runs on
EXPOSE 5002

# Run the application
CMD ["python", "pet_search_service.py"]

