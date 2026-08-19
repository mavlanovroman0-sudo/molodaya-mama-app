#!/usr/bin/env bash
# Собрать backend на сервере из git (без Docker Hub).
set -euo pipefail
cd /opt/homeease
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0
docker compose -f docker-compose.prod.yml --env-file backend/.env.production \
  build --pull=false backend
docker compose -f docker-compose.prod.yml --env-file backend/.env.production \
  up -d --no-deps --force-recreate --no-build backend
echo "OK: backend restarted"
