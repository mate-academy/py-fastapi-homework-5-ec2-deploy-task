#!/bin/bash

# Exit on error
set -e  

handle_error() {
    echo "Error: $1"
    exit 1
}

# Navigate to the directory where deploy.sh is located

cd /home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task/commands || handle_error "Failed to navigate to the application directory."

# Fetch latest changes

echo "Fetching latest changes from the repository..."
git fetch origin main || handle_error "Failed to fetch updates."

# Reset to match 'main' branch

echo "Resetting repository to match origin/main..."
git reset --hard origin/main || handle_error "Failed to reset repository."

# Fetch tags

echo "Fetching tags..."
git fetch origin --tags || handle_error "Failed to fetch tags."

# Build and run containers

docker compose -f /home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task/docker-compose-prod.yml up -d --build || handle_error "Failed to build and run Docker containers using docker-compose-prod.yml."

echo "Deployment completed successfully."
