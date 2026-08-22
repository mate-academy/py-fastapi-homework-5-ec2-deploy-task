#!/bin/bash

set -e

PROJECT_DIR="/home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task"
DEPLOY_BRANCH="develop"

handle_error() {
    echo "Error: $1"
    exit 1
}

cd "$PROJECT_DIR" || handle_error "Failed to navigate to the application directory."

echo "Fetching the latest changes from the remote repository..."
git fetch origin "$DEPLOY_BRANCH" || handle_error "Failed to fetch updates from the 'origin' remote."

echo "Switching to '$DEPLOY_BRANCH' and synchronizing with 'origin/$DEPLOY_BRANCH'..."
git checkout "$DEPLOY_BRANCH" || handle_error "Failed to switch to '$DEPLOY_BRANCH'."
git reset --hard "origin/$DEPLOY_BRANCH" || handle_error "Failed to reset the local repository to 'origin/$DEPLOY_BRANCH'."

echo "Fetching tags from the remote repository..."
git fetch origin --tags || handle_error "Failed to fetch tags from the 'origin' remote."

sudo docker compose -f docker-compose-prod.yml up -d --build --remove-orphans || handle_error "Failed to build and run Docker containers using docker-compose-prod.yml."

echo "Deployment completed successfully."
