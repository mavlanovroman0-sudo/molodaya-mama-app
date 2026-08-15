#!/usr/bin/env bash
# Один запуск на сервере: обновить код и пересобрать production.
set -euo pipefail
cd /opt/homeease
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
export COMPOSE_BAKE=false
git pull origin main
docker compose -f docker-compose.prod.yml --env-file backend/.env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file backend/.env.production exec backend bash scripts/migrate.sh
docker compose -f docker-compose.prod.yml --env-file backend/.env.production ps
echo "OK: https://my-molodaya-mama.ru"
