#!/usr/bin/env bash
# Пересобрать только сайт, без Docker Hub и без backend.
set -euo pipefail
cd /opt/homeease
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
cd frontend
docker build --pull=false -f Dockerfile.prod \
  --build-arg EXPO_PUBLIC_API_URL=https://my-molodaya-mama.ru \
  -t homeease-frontend:prod .
cd /opt/homeease
docker compose -f docker-compose.prod.yml --env-file backend/.env.production \
  up -d --no-deps --force-recreate --no-build frontend
echo "OK: https://my-molodaya-mama.ru"
