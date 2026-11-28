#!/bin/sh

echo "Waiting for MinIO to be ready..."
ATTEMPTS=0
until mc alias set minio http://"$MINIO_HOST":"$MINIO_PORT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ "$ATTEMPTS" -ge 30 ]; then
        echo "MinIO did not become ready in time."
        exit 1
    fi
    echo "MinIO is not ready yet, retrying in 3s..."
    sleep 3
done
echo "MinIO Client configured."

if mc ls minio | grep -q "$MINIO_STORAGE"; then
    echo "Bucket '$MINIO_STORAGE' already exists. Skipping creation."
else
    echo "Creating bucket: $MINIO_STORAGE"
    mc mb minio/"$MINIO_STORAGE"
fi

echo "Setting bucket policy to public..."
mc anonymous set download minio/"$MINIO_STORAGE"

echo "Getting policy info..."
mc anonymous get minio/"$MINIO_STORAGE"

echo "MinIO configuration completed!"
exit 0
