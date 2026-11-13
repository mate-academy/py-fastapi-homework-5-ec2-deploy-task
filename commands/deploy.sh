
#!/bin/bash

set -e

handle_error() {
    echo "Error: $1"
    exit 1
}

cd /home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task || handle_error "Failed to navigate to the application directory."

echo "Fetching the latest changes from the remote repository..."
git fetch origin main || handle_error "Failed to fetch updates."

echo "Resetting the local repository to origin/main..."
git reset --hard origin/main || handle_error "Failed to reset repository."

echo "Fetching tags..."
git fetch origin --tags || handle_error "Failed to fetch tags."

echo "Building and running Docker containers..."
docker compose -f docker-compose-prod.yml up -d --build || handle_error "Docker deployment failed."

echo "Deployment completed successfully."
