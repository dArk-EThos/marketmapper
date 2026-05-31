#!/bin/bash
###############################################################################
# Market Mapper — Database Backup Script
# Usage: sudo -u www-data bash backup.sh
# Cron:  0 3 * * * /opt/marketmapper/deploy/backup.sh
###############################################################################
set -euo pipefail

BACKUP_DIR="/opt/marketmapper/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="marketmapper_${TIMESTAMP}.sql"

# Create backup directory if needed
mkdir -p "${BACKUP_DIR}"

# Dump database using Django's DATABASE_URL
# Source the .env to get DATABASE_URL, then use it directly with pg_dump
set -a
source /opt/marketmapper/.env
set +a

# pg_dump can accept a connection URI directly
pg_dump "${DATABASE_URL}" > "${BACKUP_DIR}/${BACKUP_FILE}"

# Keep only last 30 backups
ls -1t "${BACKUP_DIR}"/marketmapper_*.sql 2>/dev/null | tail -n +31 | xargs -r rm --

echo "Backup saved: ${BACKUP_DIR}/${BACKUP_FILE} ($(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1))"
