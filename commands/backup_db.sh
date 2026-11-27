#!/bin/bash

# Dumps the PostgreSQL database from the running container to a gzipped file.
# Usage: bash commands/backup_db.sh
# Cron example (daily at 03:00):
#   0 3 * * * bash /root/src/mate-fastapi-homework-5/commands/backup_db.sh

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/src/mate-fastapi-homework-5}"
BACKUP_DIR="${BACKUP_DIR:-/root/backups}"
CONTAINER="${DB_CONTAINER:-postgres_theater}"
KEEP_DAYS="${KEEP_DAYS:-7}"

# Load POSTGRES_USER / POSTGRES_DB from the project's .env
set -a
# shellcheck disable=SC1091
source "$PROJECT_DIR/.env"
set +a

mkdir -p "$BACKUP_DIR"
FILE="$BACKUP_DIR/${POSTGRES_DB}_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "Creating backup: $FILE"
docker exec "$CONTAINER" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$FILE"

# Remove backups older than KEEP_DAYS days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +"$KEEP_DAYS" -delete

echo "Backup completed successfully."
