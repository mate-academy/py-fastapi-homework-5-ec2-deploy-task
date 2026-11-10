#!/bin/bash

set -e

APP_DIR="/home/ubuntu/py-fastapi-homework-5-ec2-deploy-task"
BRANCH="dev-py-fastapi-homework-5-ec2-deploy-task"
LOCK_FILE="/tmp/theater-api-deploy.lock"

cd "$APP_DIR"

(
    flock -n 9 || exit 0

    git fetch origin "$BRANCH"

    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse FETCH_HEAD)

    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        exit 0
    fi

    echo "New commit detected. Starting deployment..."

    bash commands/deploy.sh
) 9>"$LOCK_FILE"