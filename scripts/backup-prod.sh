#!/usr/bin/env bash
# Полная копия production: база + секреты + SSL.
# Контейнеры не останавливает, образы не собирает, сайт не обновляет.
set -euo pipefail

ROOT=/opt/homeease
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="${ROOT}/backups/${STAMP}"
PG_CONTAINER=homeease-prod-postgres

cd "${ROOT}"

mkdir -p "${DEST}"
chmod 700 "${ROOT}/backups" "${DEST}"

if ! docker inspect -f '{{.State.Running}}' "${PG_CONTAINER}" 2>/dev/null | grep -qx true; then
  echo "ERROR: контейнер ${PG_CONTAINER} не запущен. Копия не начата. Сайт не менялся."
  exit 1
fi

docker exec "${PG_CONTAINER}" sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/homeease.dump'
docker cp "${PG_CONTAINER}:/tmp/homeease.dump" "${DEST}/postgres.dump"
docker exec "${PG_CONTAINER}" rm -f /tmp/homeease.dump
chmod 600 "${DEST}/postgres.dump"

if [ ! -f "${ROOT}/backend/.env.production" ]; then
  echo "ERROR: нет файла ${ROOT}/backend/.env.production. Копия базы уже лежит в ${DEST}. Сайт не менялся."
  exit 1
fi
cp -a "${ROOT}/backend/.env.production" "${DEST}/env.production"
chmod 600 "${DEST}/env.production"

if [ -d "${ROOT}/docs/ssl" ]; then
  cp -a "${ROOT}/docs/ssl" "${DEST}/ssl"
fi

SIZE="$(wc -c < "${DEST}/postgres.dump" | tr -d ' ')"
if [ "${SIZE}" -lt 1024 ]; then
  echo "ERROR: файл копии слишком маленький (${SIZE} байт). Сайт не менялся. Папку ${DEST} не удаляйте."
  exit 1
fi

echo "BACKUP_OK"
echo "FOLDER=${DEST}"
echo "DUMP_BYTES=${SIZE}"
ls -lh "${DEST}"

if command -v curl >/dev/null 2>&1; then
  CODE="$(curl -s -o /dev/null -w '%{http_code}' https://my-molodaya-mama.ru || echo FAIL)"
  echo "SITE=${CODE}"
fi
