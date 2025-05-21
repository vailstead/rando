## Dockerfile
```
# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port
EXPOSE 8000

# Run the app
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]

```

## Docker compose file
```
version: '3.9'

services:
  web:
    build: .
    container_name: app
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis

  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"

  celery:
    build: .
    container_name: celery
    command: celery -A myproject worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - web
      - redis
```
