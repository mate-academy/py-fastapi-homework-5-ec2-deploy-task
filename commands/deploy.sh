#!/usr/bin/env bash
set -euo pipefail

# Systems Manager runs this script on EC2 with the revision tested by CI.
# For a manual run, locate the checkout relative to this file.
if [[ $# -ge 2 ]]; then
    cd -- "$2"
else
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
fi

exec 9>"$(git rev-parse --git-dir)/ec2-deploy.lock"
flock 9
git fetch origin refs/heads/main
latest=$(git rev-parse FETCH_HEAD)
revision=${1:-$latest}
if [[ "$revision" != "$latest" ]]; then
    echo "The tested revision is no longer the tip of main." >&2
    exit 1
fi
if ! git diff --quiet HEAD --; then
    echo "The server checkout has uncommitted changes." >&2
    exit 1
fi
git checkout --detach "$revision"
docker compose -f docker-compose-prod.yml up -d --build
curl --fail --silent --show-error --retry 45 --retry-all-errors \
    --retry-delay 2 --max-time 5 --output /dev/null \
    'http://127.0.0.1/api/v1/theater/movies/?per_page=1'
printf 'Deployed %s. The movie catalogue is responding.\n' "$revision"
