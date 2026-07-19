#!/usr/bin/env bash

set -Eeuo pipefail

APP_DIR="/home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task"
COMPOSE_FILE="docker-compose-prod.yml"

handle_error() {
    echo "❌ Error: $1"
    exit 1
}

echo "📂 Navigating to application directory..."
cd "$APP_DIR" || handle_error "Failed to navigate to $APP_DIR."

echo "📥 Fetching latest changes..."
git fetch origin main --tags || handle_error "Failed to fetch updates."

echo "🔄 Resetting repository..."
git reset --hard origin/main || handle_error "Failed to reset repository."

echo "🐳 Building and starting containers..."
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans \
    || handle_error "Docker Compose deployment failed."

echo "🧹 Removing unused images..."
docker image prune -f

echo "✅ Deployment completed successfully."