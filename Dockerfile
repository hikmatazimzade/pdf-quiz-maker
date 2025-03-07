# Use official Python image as base
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the new working directory in the container
WORKDIR /app/main_project

# Expose the port Django runs on
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "main_project.wsgi:application", "--bind", "0.0.0.0:8000"]