#!/usr/bin/env bash
# Применение SQL-миграций HomeEase 2.0 (все .sql из backend/db/migrations/ по порядку)
#
# Production (Docker):
#   docker compose -f docker-compose.prod.yml exec backend bash scripts/migrate.sh
#
# Локально:
#   POSTGRES_HOST=localhost POSTGRES_PASSWORD=... bash scripts/migrate.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS_DIR="${SCRIPT_DIR}/../db/migrations"

# В Docker Compose сервис БД называется postgres; локально — localhost
if [ -z "${POSTGRES_HOST:-}" ]; then
  if [ "${APP_ENV:-}" = "production" ] || echo "${DATABASE_URL:-}" | grep -q "@postgres:"; then
    DB_HOST="postgres"
  else
    DB_HOST="localhost"
  fi
else
  DB_HOST="${POSTGRES_HOST}"
fi
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-homeease}"
DB_NAME="${POSTGRES_DB:-homeease}"
DB_PASSWORD="${POSTGRES_PASSWORD:-homeease_dev}"

export PGPASSWORD="${DB_PASSWORD}"

echo "Applying migrations from ${MIGRATIONS_DIR} to ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

shopt -s nullglob
files=("${MIGRATIONS_DIR}"/*.sql)
IFS=$'\n' sorted=($(sort <<<"${files[*]}"))
unset IFS

if [ ${#sorted[@]} -eq 0 ]; then
  echo "No .sql migration files found."
  exit 0
fi

for f in "${sorted[@]}"; do
  echo ">> $(basename "$f")"
  psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
done

echo "Migrations applied successfully."
