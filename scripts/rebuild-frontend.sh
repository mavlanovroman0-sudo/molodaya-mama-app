#!/usr/bin/env bash
# Собрать сайт из готовых файлов (без node и без Docker Hub).
set -euo pipefail
cd /opt/homeease
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
cd frontend
docker build --pull=false -f Dockerfile.nginx -t homeease-frontend:prod .
cd /opt/homeease
docker compose -f docker-compose.prod.yml --env-file backend/.env.production \
  up -d --no-deps --force-recreate --no-build frontend
echo "OK: https://my-molodaya-mama.ru"
