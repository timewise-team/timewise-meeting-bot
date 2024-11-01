#!/bin/bash

git pull

# Variables
IMAGE_NAME="meeting-bot"
CONTAINER_NAME="meeting-bot-container"
RABBITMQ_HOST="localhost"  # Change this if your RabbitMQ server is hosted elsewhere

# Step 1: Build the Docker image
echo "Building the Docker image..."
docker build -t $IMAGE_NAME .

# Check if the build succeeded
if [ $? -ne 0 ]; then
    echo "Docker build failed. Exiting."
    exit 1
fi
echo "Docker image built successfully."

# Step 2: Stop and remove any existing container with the same name
echo "Stopping any existing container..."
docker stop $CONTAINER_NAME >/dev/null 2>&1
docker rm $CONTAINER_NAME >/dev/null 2>&1
echo "Removed existing container (if any)."

# Step 3: Run the Docker container
echo "Starting the Docker container..."
docker run -d \
  --name $CONTAINER_NAME \
  --network="host" \
  -e RABBITMQ_HOST=$RABBITMQ_HOST \
  $IMAGE_NAME

# Check if the container started successfully
if [ $? -ne 0 ]; then
    echo "Failed to start Docker container. Exiting."
    exit 1
fi
echo "Docker container started successfully."

# Step 4: Display container logs
echo "Displaying container logs..."
docker logs -f $CONTAINER_NAME
