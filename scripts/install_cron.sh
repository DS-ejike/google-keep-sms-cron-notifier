#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="${PROJECT_DIR}/scripts/run_keep_sms_notifier.sh"
SCHEDULE="${SCHEDULE:-*/5 * * * *}"
MARKER="# keep-sms-cron"
ENTRY="${SCHEDULE} ${RUNNER} ${MARKER}"

chmod +x "${RUNNER}"

existing_cron="$(mktemp)"
new_cron="$(mktemp)"
trap 'rm -f "${existing_cron}" "${new_cron}"' EXIT

crontab -l > "${existing_cron}" 2>/dev/null || true
grep -v "${MARKER}" "${existing_cron}" > "${new_cron}" || true
printf '%s\n' "${ENTRY}" >> "${new_cron}"
crontab "${new_cron}"

echo "Installed cron entry:"
echo "${ENTRY}"

