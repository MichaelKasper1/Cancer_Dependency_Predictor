# 1. Use an official Python runtime as a parent image
FROM python:3.8-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Install system dependencies for your app
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Install any dependencies that are defined in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire application code to the container
COPY . /app

# 6. Set environment variables (optional)
# Set the Django settings module for production or development (adjust accordingly)
ENV DJANGO_SETTINGS_MODULE=your_project_name.settings.production

# 7. Expose port (usually 8000 for Django)
EXPOSE 8000

# 8. Run the Django server using gunicorn for production
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]