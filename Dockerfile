# Use Python 3.13 slim image
FROM python:3.13-slim
LABEL authors="Matija Slivonja"

# Set working directory inside container
WORKDIR /app

# Copy requirement list first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py weather.py s3_storage.py templates/ static/ /app/

# Expose internal container port 5000
EXPOSE 5000

# Run the app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]