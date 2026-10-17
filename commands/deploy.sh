#!/bin/bash

# Exit immediately if any command fails
set -e

handle_error() {
    echo "Error: $1"
    exit 1
}

PROJECT_DIR=/home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task

cd "$PROJECT_DIR" || handle_error "Failed to navigate to the project directory."

echo "Fetching the latest changes from the remote repository..."
git fetch origin main || handle_error "Failed to fetch updates from 'origin'."

echo "Switching to 'main' and resetting it to match 'origin/main'..."
git checkout -f -B main origin/main || handle_error "Failed to reset to 'origin/main'."

echo "Building and starting Docker containers..."
docker compose -f docker-compose-prod.yml up -d --build \
    || handle_error "Failed to build and run containers."

echo "Deployment completed successfully."