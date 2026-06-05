#!/usr/bin/env bash
# Skål — Interactive Setup Script
# Walks through .env configuration and optionally launches the app.

set -e

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

say()  { echo -e "${CYAN}${BOLD}▶${RESET} $*"; }
ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }
err()  { echo -e "${RED}✗${RESET}  $*" >&2; }

prompt() {
    # prompt <varname> <label> [default]
    local var="$1" label="$2" default="$3" value
    if [[ -n "$default" ]]; then
        read -rp "$(echo -e "  ${BOLD}${label}${RESET} [${default}]: ")" value
        value="${value:-$default}"
    else
        while [[ -z "$value" ]]; do
            read -rp "$(echo -e "  ${BOLD}${label}${RESET}: ")" value
            [[ -z "$value" ]] && warn "This field is required."
        done
    fi
    printf -v "$var" '%s' "$value"
}

prompt_secret() {
    # prompt_secret <varname> <label>
    local var="$1" label="$2" value confirm
    while true; do
        read -rsp "$(echo -e "  ${BOLD}${label}${RESET}: ")" value; echo
        [[ -z "$value" ]] && { warn "This field is required."; continue; }
        read -rsp "$(echo -e "  ${BOLD}Confirm ${label}${RESET}: ")" confirm; echo
        [[ "$value" == "$confirm" ]] && break
        warn "Values do not match. Try again."
    done
    printf -v "$var" '%s' "$value"
}

hr() { echo -e "${CYAN}────────────────────────────────────────────────────────${RESET}"; }

# ── Header ────────────────────────────────────────────────────────────────────
clear
hr
echo -e "${BOLD}${CYAN}  🍯  Skål — Setup Wizard${RESET}"
echo -e "  This will create your ${BOLD}.env${RESET} file and (optionally) start the app."
hr
echo

# ── Check dependencies ────────────────────────────────────────────────────────
say "Checking dependencies..."

if ! command -v docker &>/dev/null; then
    err "Docker not found. Install Docker before continuing."
    err "https://docs.docker.com/get-docker/"
    exit 1
fi
ok "Docker found: $(docker --version | head -1)"

if ! docker compose version &>/dev/null 2>&1; then
    err "Docker Compose (v2) not found. Update Docker Desktop or install the compose plugin."
    exit 1
fi
ok "Docker Compose found: $(docker compose version | head -1)"

if ! command -v python3 &>/dev/null; then
    err "python3 not found — needed to generate a SECRET_KEY."
    exit 1
fi
ok "python3 found"
echo

# ── Existing install detection ────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
    hr
    echo -e "${BOLD}  Existing installation detected${RESET}"
    hr
    echo "  A .env file already exists, which means Skål may already be installed."
    echo
    echo -e "  ${BOLD}A${RESET}  Upgrade  — back up data, rebuild with new code, apply migrations"
    echo -e "  ${BOLD}B${RESET}  Reconfigure — overwrite .env and do a fresh setup (${RED}data stays in DB volume${RESET})"
    echo
    read -rp "  $(echo -e "${BOLD}Choice${RESET} [A/b]: ")" install_choice
    install_choice="${install_choice:-A}"
    echo

    if [[ "${install_choice,,}" != "b" ]]; then
        say "Launching upgrade script…"
        exec "$SCRIPT_DIR/upgrade.sh"
    fi

    warn "Reconfiguring — the existing .env will be overwritten."
    echo
fi

# ── Secret key ────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  1 / 5 — Secret Key${RESET}"
hr
echo "  A cryptographically random key will be generated for you."
echo "  You can also paste your own (leave blank to auto-generate)."
echo
read -rp "  $(echo -e "${BOLD}SECRET_KEY${RESET} [auto-generate]: ")" SECRET_KEY
if [[ -z "$SECRET_KEY" ]]; then
    SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
    ok "Generated: ${SECRET_KEY:0:20}…"
else
    ok "Using provided key."
fi
echo

# ── Debug mode ────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  2 / 5 — Debug Mode${RESET}"
hr
echo "  Set to True only for local development. Never True in production."
echo
read -rp "  $(echo -e "${BOLD}DEBUG${RESET} [False]: ")" DEBUG
DEBUG="${DEBUG:-False}"
[[ "$DEBUG" == "1" || "${DEBUG,,}" == "true" ]] && DEBUG="True" || DEBUG="False"
ok "DEBUG=$DEBUG"
echo

# ── Database ──────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  3 / 5 — Data Storage${RESET}"
hr
echo "  Skål stores your recipes and batches in a private database."
echo "  These credentials are only used internally — you won't need them again"
echo "  unless you're restoring a backup or connecting an external tool."
echo
prompt POSTGRES_DB   "Database name"     "skal"
prompt POSTGRES_USER "Database user"     "skaluser"
prompt_secret POSTGRES_PASSWORD "Database password"
echo
ok "Storage configured: $POSTGRES_DB"
echo

# ── Allowed hosts ─────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  4 / 5 — Access & Networking${RESET}"
hr
echo "  The hostname or IP address users will use to reach Skål."
echo "  Use 'localhost' for local use, or your server's domain/IP for remote access."
echo "  Multiple values can be comma-separated: e.g. myserver.com,192.168.1.10"
echo
prompt DJANGO_ALLOWED_HOSTS "Hostname or IP address" "localhost,127.0.0.1"
prompt HOST_PORT "Port number" "8000"
echo
ok "Address: $DJANGO_ALLOWED_HOSTS"
ok "Port:    $HOST_PORT"
echo

# ── Superuser ─────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  5 / 5 — Admin Account${RESET}"
hr
echo "  This account is created automatically on first run."
echo "  Use it to log in and manage the app."
echo
prompt DJANGO_SUPERUSER_USERNAME "Username" "admin"
prompt DJANGO_SUPERUSER_EMAIL    "Email address" ""
prompt_secret DJANGO_SUPERUSER_PASSWORD "Password"
echo
ok "Admin account: $DJANGO_SUPERUSER_USERNAME <$DJANGO_SUPERUSER_EMAIL>"
echo

# ── Summary ───────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  Summary${RESET}"
hr
echo -e "  Secret key          ${GREEN}${SECRET_KEY:0:20}…${RESET}"
echo -e "  Debug mode          ${DEBUG}"
echo -e "  Database name       ${POSTGRES_DB}"
echo -e "  Database user       ${POSTGRES_USER}"
echo -e "  Database password   ${RED}(hidden)${RESET}"
echo -e "  Hostname / IP       ${DJANGO_ALLOWED_HOSTS}"
echo -e "  Port                ${HOST_PORT}"
echo -e "  Admin username      ${DJANGO_SUPERUSER_USERNAME}"
echo -e "  Admin email         ${DJANGO_SUPERUSER_EMAIL}"
echo -e "  Admin password      ${RED}(hidden)${RESET}"
hr
echo
read -rp "  Write .env and continue? [Y/n] " confirm
[[ "${confirm,,}" == "n" ]] && { say "Aborted — no files written."; exit 0; }
echo

# ── Write .env ────────────────────────────────────────────────────────────────
cat > "$ENV_FILE" <<EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=${DEBUG}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
EOF

ok ".env written to $ENV_FILE"

# ── Update docker-compose port if non-default ─────────────────────────────────
if [[ "$HOST_PORT" != "8000" ]]; then
    # Patch the ports line in docker-compose.yml
    if command -v sed &>/dev/null; then
        sed -i "s|\"8000:8000\"|\"${HOST_PORT}:8000\"|g" "$SCRIPT_DIR/docker-compose.yml"
        ok "docker-compose.yml updated to port $HOST_PORT"
    else
        warn "Could not update docker-compose.yml automatically."
        warn "Manually change the ports line to \"${HOST_PORT}:8000\"."
    fi
fi
echo

# ── Launch? ───────────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}  Launch Skål?${RESET}"
hr
echo "  This will run: docker compose up --build -d"
echo "  Migrations and superuser creation happen automatically on first start."
echo
read -rp "  Start the app now? [Y/n] " launch
if [[ "${launch,,}" != "n" ]]; then
    echo
    say "Building and starting containers…"
    echo
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" up --build -d
    echo
    hr
    ok "Skål is running!"
    echo
    echo -e "  Open ${BOLD}${CYAN}http://localhost:${HOST_PORT}${RESET} in your browser."
    echo -e "  Login with username: ${BOLD}${DJANGO_SUPERUSER_USERNAME}${RESET}"
    echo
    echo -e "  To stop:   ${BOLD}docker compose down${RESET}"
    echo -e "  To logs:   ${BOLD}docker compose logs -f web${RESET}"
    hr
else
    echo
    say "When you're ready, run:"
    echo -e "  ${BOLD}docker compose up --build -d${RESET}"
    echo
fi
