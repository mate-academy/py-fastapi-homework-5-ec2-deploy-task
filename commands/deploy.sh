#!/bin/bash
set -e

cd /home/ubuntu/src/py-fastapi-homework-5-ec2-deploy-task

git fetch origin main
git reset --hard origin/main
git fetch --tags

docker compose -f docker-compose-prod.yml up -d --build

echo "Deployment completed successfully"
