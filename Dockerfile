# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    nodejs \
    npm \
    certbot \
    python3-certbot-nginx \
    bind9-dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Tailwind CSS globally
RUN npm install -g tailwindcss

# Expose port 8080 to the outside world
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload", "--ssl-keyfile", "key.pem", "--ssl-certfile", "cert.pem"]

