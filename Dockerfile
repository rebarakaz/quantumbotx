# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements-docker.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV BROKER_TYPE=CCXT 
# Default to CCXT in Docker since MT5 doesn't run on Linux easily

# Run run.py when the container launches
CMD ["python", "run.py"]
