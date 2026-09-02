#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

LOCK_FILE="${LOCK_FILE:-${PROJECT_DIR}/.state/keep-sms-cron.lock}"
LOG_FILE="${LOG_FILE:-${PROJECT_DIR}/.state/keep-sms-cron.log}"
PYTHON_BIN="${PYTHON_BIN:-${PROJECT_DIR}/.venv/bin/python}"

mkdir -p "$(dirname "${LOCK_FILE}")" "$(dirname "${LOG_FILE}")"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="python3"
fi

cd "${PROJECT_DIR}"
if command -v flock >/dev/null 2>&1; then
  flock -n "${LOCK_FILE}" "${PYTHON_BIN}" -m keep_sms_cron --once >> "${LOG_FILE}" 2>&1
else
  "${PYTHON_BIN}" -m keep_sms_cron --once >> "${LOG_FILE}" 2>&1
fi
