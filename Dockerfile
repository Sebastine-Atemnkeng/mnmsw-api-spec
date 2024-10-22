# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install any necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file first for better caching
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and static files into the container
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Expose the port the app runs on
EXPOSE 8000

# Set the command to run the application using Waitress
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8000", "app:app"]
