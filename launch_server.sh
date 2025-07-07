#!/bin/bash
set -euo pipefail

cd /home/musava/cijeneorg2

git fetch --all
git reset --hard origin/main

docker compose pull
docker compose up -d --build --remove-orphans
