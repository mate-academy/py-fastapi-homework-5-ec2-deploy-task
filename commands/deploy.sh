#!/bin/bash

set -euo pipefail

handle_error() {
    echo "Error: $1"
    exit 1
}

APP_DIR="${APP_DIR:-/home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"

echo "Deploying branch '$DEPLOY_BRANCH' from '$APP_DIR'..."

cd "$APP_DIR" || handle_error "Failed to navigate to the application directory."

echo "Fetching the latest changes from origin/$DEPLOY_BRANCH..."
git fetch origin "$DEPLOY_BRANCH" || handle_error "Failed to fetch updates from the 'origin' remote."

echo "Resetting the local repository to match origin/$DEPLOY_BRANCH..."
git reset --hard "origin/$DEPLOY_BRANCH" || handle_error "Failed to reset the local repository."

echo "Fetching tags from the remote repository..."
git fetch origin --tags || handle_error "Failed to fetch tags from the 'origin' remote."

echo "Building and restarting Docker containers..."
docker compose -f docker-compose-prod.yml up -d --build --remove-orphans || handle_error "Failed to start Docker Compose."

echo "Deployment completed successfully."
