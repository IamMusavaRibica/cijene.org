#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")" || exit 1

git fetch --all
git reset --hard origin/main

docker compose pull
docker compose up -d --build --remove-orphans
