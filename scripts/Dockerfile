# Multi-stage data pipeline for Estonian traffic and mortality statistics
# Base image: Python 3.11 slim
FROM python:3.11-slim

# Install CA certificates for HTTPS (needed for corporate proxies)
RUN apt-get update && apt-get install -y ca-certificates && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variable for SSL certificate validation
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Set working directory inside container
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python scripts and data files
COPY . .

# Copy entrypoint script (runs all data downloads)
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set entrypoint to run all scripts sequentially
ENTRYPOINT ["/entrypoint.sh"]
