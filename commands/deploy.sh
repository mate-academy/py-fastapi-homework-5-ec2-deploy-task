#!/bin/bash

set -e

APP_DIR="/home/ubuntu/py-fastapi-homework-5-ec2-deploy-task"
BRANCH="dev-py-fastapi-homework-5-ec2-deploy-task"

cd "$APP_DIR"

echo "Fetching latest changes..."
git fetch origin "$BRANCH"

echo "Updating application code..."
git reset --hard "origin/$BRANCH"

echo "Running database migrations..."
docker compose -f docker-compose-prod.yml run --rm --no-deps migrator

echo "Restarting backend..."
docker compose -f docker-compose-prod.yml restart web

echo "Deployment completed successfully."
