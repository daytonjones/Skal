#!/usr/bin/env bash
# Skål — Upgrade Script
# Backs up the database, rebuilds containers with the new image,
# then runs migrations. Safe to run on any v1 → v2 (or any future) upgrade.

set -e

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

say()  { echo -e "${CYAN}${BOLD}▶${RESET} $*"; }
ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }
err()  { echo -e "${RED}✗${RESET}  $*" >&2; }
hr()   { echo -e "${CYAN}────────────────────────────────────────────────────────${RESET}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
BACKUP_DIR="$SCRIPT_DIR/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/skal_backup_${TIMESTAMP}.sql"

# ── Header ────────────────────────────────────────────────────────────────────
clear
hr
echo -e "${BOLD}${CYAN}  🍯  Skål — Upgrade${RESET}"
echo -e "  This will back up your data, rebuild the app, and apply any new migrations."
hr
echo

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if [[ ! -f "$ENV_FILE" ]]; then
    err "No .env file found. Run ./install.sh first."
    exit 1
fi

if ! command -v docker &>/dev/null; then
    err "Docker not found."
    exit 1
fi

if ! docker compose version &>/dev/null 2>&1; then
    err "Docker Compose (v2) not found."
    exit 1
fi

source "$ENV_FILE" 2>/dev/null || true

if [[ -z "$POSTGRES_DB" || -z "$POSTGRES_USER" || -z "$POSTGRES_PASSWORD" ]]; then
    err ".env is missing database credentials. Cannot continue safely."
    exit 1
fi

ok "Pre-flight checks passed"
echo

# ── Confirm ───────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  What this upgrade does:${RESET}"
echo "  1. Creates a database backup at: backups/skal_backup_${TIMESTAMP}.sql"
echo "  2. Rebuilds the Docker image with the latest code"
echo "  3. Restarts containers and applies any new database migrations"
echo
warn "Your data will NOT be deleted. The backup is a safety net."
echo
read -rp "  Proceed with upgrade? [Y/n] " confirm
[[ "${confirm,,}" == "n" ]] && { say "Aborted."; exit 0; }
echo

# ── Backup ────────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  Step 1 / 3 — Database Backup${RESET}"
hr
mkdir -p "$BACKUP_DIR"
say "Backing up database to $BACKUP_FILE …"

if docker compose -f "$SCRIPT_DIR/docker-compose.yml" ps skal_db | grep -q "running\|Up"; then
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T skal_db \
        pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_FILE"
    ok "Backup saved: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
else
    warn "Database container is not running — skipping backup."
    warn "If you want a backup first, start the containers and re-run this script."
    read -rp "  Continue without a backup? [y/N] " skip_backup
    [[ "${skip_backup,,}" != "y" ]] && { say "Aborted."; exit 0; }
fi
echo

# ── Rebuild ───────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  Step 2 / 3 — Rebuild & Restart${RESET}"
hr
say "Rebuilding image and restarting containers…"
echo
docker compose -f "$SCRIPT_DIR/docker-compose.yml" up --build -d
echo
ok "Containers rebuilt and running"
echo

# ── Verify migrations ran ─────────────────────────────────────────────────────
hr
echo -e "${BOLD}  Step 3 / 3 — Verify${RESET}"
hr
say "Waiting a moment for the app to finish starting…"
sleep 8
say "Checking migration status…"
docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T web \
    python manage.py showmigrations --plan 2>/dev/null | tail -10 || true
echo

# ── Done ──────────────────────────────────────────────────────────────────────
hr
ok "Upgrade complete!"
echo
echo -e "  Your backup is at: ${BOLD}${BACKUP_FILE}${RESET}"
echo
echo -e "  ${BOLD}To restore from backup if anything went wrong:${RESET}"
echo -e "    docker compose exec -T skal_db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < ${BACKUP_FILE}"
echo
echo -e "  To view logs: ${BOLD}docker compose logs -f web${RESET}"
hr
