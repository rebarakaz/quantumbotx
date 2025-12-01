# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies (git only for potential future use)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies with a generous timeout
ENV PIP_DEFAULT_TIMEOUT=120

# Copy pandas_ta stub for compatibility
COPY pandas_ta_stub /app/pandas_ta_stub

# Install dependencies and pandas_ta stub
RUN python -m pip install --upgrade pip && \
    pip install /app/pandas_ta_stub && \
    pip install --no-cache-dir -r requirements-docker.txt

ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV BROKER_TYPE=CCXT
# Default to CCXT in Docker since MT5 doesn't run on Linux easily

# Run run.py when the container launches
CMD ["python", "run.py"]
