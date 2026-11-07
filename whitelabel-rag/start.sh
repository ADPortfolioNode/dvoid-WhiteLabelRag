#!/usr/bin/env bash
set -euo pipefail

# WhiteLabelRAG one-command startup (Docker Compose).
# Same pattern as the other projects: one command, persistent data
# (named volumes are never wiped by this script), silo-safe ports.
#
# Usage: ./start.sh [--build] [--no-build] [--test] [--down]
#   (default)  start the stack (cached build; builds if the image is missing)
#   --build    forced --no-cache rebuild, then start
#   --no-build start without building (same as the default, explicit)
#   --test     monitored startup: wait for /health and report PASS/FAIL
#   --down     stop the stack (data is kept in the named volumes)
#
# Run from the whitelabel-rag folder (where this file lives) in Git Bash.
# Needs Docker Desktop running and a .env file with GEMINI_API_KEY set.
# If port 5000 is held by another app, the host port bumps to 5001..5010
# and the app still starts; a stale WhiteLabelRAG container is stopped
# instead and the port is kept.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# shellcheck source=scripts/resolve_host_ports.sh
. "${SCRIPT_DIR}/scripts/resolve_host_ports.sh"

COMPOSE_FILE="docker-compose.yml"
APP_CONTAINER="whitelabel-rag-app"
COMPOSE_CMD_ARRAY=()
COMPOSE_CMD=""

choose_compose_command() {
    # Prefer 'docker compose' (v2) but fall back to 'docker-compose' (v1).
    if command docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD_ARRAY=(docker compose -f "${COMPOSE_FILE}")
    elif command -v docker-compose >/dev/null 2>&1 && command docker-compose version >/dev/null 2>&1; then
        COMPOSE_CMD_ARRAY=(docker-compose -f "${COMPOSE_FILE}")
    else
        echo "ERROR: Neither 'docker compose' nor 'docker-compose' is available." >&2
        echo "Install Docker Desktop (https://www.docker.com/products/docker-desktop) and make sure it is running." >&2
        exit 1
    fi
    COMPOSE_CMD="${COMPOSE_CMD_ARRAY[*]}"
}

compose_cmd() {
    if [ "${#COMPOSE_CMD_ARRAY[@]}" -eq 0 ]; then
        choose_compose_command
    fi
    "${COMPOSE_CMD_ARRAY[@]}" "$@"
}

check_docker() {
    echo "Checking Docker..."
    if ! command -v docker >/dev/null 2>&1; then
        echo "ERROR: 'docker' command not found." >&2
        echo "Install Docker Desktop (https://www.docker.com/products/docker-desktop) and restart your shell." >&2
        exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
        echo "ERROR: Could not connect to the Docker daemon." >&2
        echo "Start Docker Desktop and wait for it to finish starting, then run ./start.sh again." >&2
        exit 1
    fi
    echo "✓ Docker daemon is responsive."
}

check_env() {
    # Compose reads .env itself for interpolation; load it here too so
    # the port resolver sees a preset PORT and we can check the key.
    if [ -f .env ]; then
        set -a
        # shellcheck disable=SC1091
        . ./.env
        set +a
    fi
    if [ -z "${GEMINI_API_KEY:-}" ]; then
        echo "ERROR: GEMINI_API_KEY is not set." >&2
        echo "The app cannot answer questions without a Google Gemini key." >&2
        echo "  1. Get a key: https://aistudio.google.com/app/apikey" >&2
        echo "  2. Create whitelabel-rag/.env with this line (never share the key):" >&2
        echo "       GEMINI_API_KEY=<redacted>" >&2
        exit 1
    fi
}

# Wait for the app container to be healthy (or at least Up), then for
# the HTTP health endpoint. Returns 0 on success, 1 on timeout/failure.
wait_for_app() {
    local port="$1" max_checks="${2:-36}" interval="${3:-5}"
    local i status health
    echo "Waiting for ${APP_CONTAINER} to be ready (timeout $((max_checks * interval))s)..."
    for i in $(seq 1 "${max_checks}"); do
        status=$(docker ps -a --filter "name=${APP_CONTAINER}" --format "{{.Status}}" 2>/dev/null | head -n1 || true)
        if echo "${status}" | grep -qE "Exited|Dead"; then
            echo "✗ ERROR: ${APP_CONTAINER} has exited unexpectedly." >&2
            echo "--- LOGS ---" >&2
            docker logs "${APP_CONTAINER}" --tail 100 >&2 || true
            return 1
        fi
        health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "${APP_CONTAINER}" 2>/dev/null || true)
        if [ "${health}" = "healthy" ]; then
            echo "✓ ${APP_CONTAINER} is healthy."
            break
        fi
        if [ "${health}" = "unhealthy" ]; then
            echo "✗ ERROR: ${APP_CONTAINER} has become unhealthy." >&2
            docker logs "${APP_CONTAINER}" --tail 100 >&2 || true
            return 1
        fi
        if echo "${status}" | grep -qi "Up" && [ -z "${health}" ]; then
            echo "✓ ${APP_CONTAINER} is Up (no healthcheck reported yet)."
            break
        fi
        if [ "$i" -eq "${max_checks}" ]; then
            echo "✗ ERROR: Timed out waiting for ${APP_CONTAINER} to become ready." >&2
            compose_cmd ps >&2 || true
            compose_cmd logs --tail 100 >&2 || true
            return 1
        fi
        sleep "${interval}"
    done

    echo "Waiting for http://127.0.0.1:${port}/health ..."
    for i in $(seq 1 "${max_checks}"); do
        if curl -s -f --max-time "${interval}" "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
            echo "✓ App answers /health."
            return 0
        fi
        if [ "$i" -eq "${max_checks}" ]; then
            echo "✗ ERROR: Timed out waiting for /health on port ${port}." >&2
            compose_cmd logs --tail 100 >&2 || true
            return 1
        fi
        sleep "${interval}"
    done
}

print_success() {
    local port="$1"
    echo ""
    echo "================================================="
    echo "✓ WhiteLabelRAG Started Successfully"
    echo "================================================="
    echo ""
    echo "  App: http://127.0.0.1:${port}"
    echo "  Health: http://127.0.0.1:${port}/health"
    echo ""
    echo "Container status:"
    compose_cmd ps
    echo ""
    echo "To view live logs, run:"
    echo "  ${COMPOSE_CMD} logs -f"
    echo "To stop (data is kept), run:"
    echo "  ./start.sh --down"
}

# --- Flags ---
BUILD=false
DOWN=false
TEST_REQUESTED=false

while [ "${#}" -gt 0 ]; do
    case "$1" in
        --build) BUILD=true; shift ;;
        --no-build) BUILD=false; shift ;;
        --down) DOWN=true; shift ;;
        --test) TEST_REQUESTED=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--build] [--no-build] [--test] [--down]"
            echo "  (default)  start the stack"
            echo "  --build    forced --no-cache rebuild, then start"
            echo "  --no-build start without building (default)"
            echo "  --test     monitored startup: wait for /health, report PASS/FAIL"
            echo "  --down     stop the stack (data is kept)"
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; echo "Usage: $0 [--build] [--no-build] [--test] [--down]" >&2; exit 2 ;;
    esac
done

choose_compose_command

if [ "${DOWN}" = true ]; then
    echo "Stopping WhiteLabelRAG (data is kept in the named volumes)..."
    compose_cmd down --remove-orphans
    echo "✓ Stack is down."
    exit 0
fi

check_docker
check_env
echo ""

resolve_compose_host_ports || {
    echo "ERROR: Unable to resolve host ports." >&2
    exit 1
}
echo "App host port: ${PORT}"

echo "Stopping any running WhiteLabelRAG containers to clear ports..."
compose_cmd down --remove-orphans 2>/dev/null || true
sleep 2

# Re-check right before starting: a holder may have appeared meanwhile.
resolve_compose_host_ports || {
    echo "ERROR: Unable to resolve host ports." >&2
    exit 1
}

if [ "${BUILD}" = true ]; then
    echo "Building image with --no-cache..."
    if ! compose_cmd build --no-cache; then
        echo "ERROR: Build failed." >&2
        exit 1
    fi
fi

echo "Starting services..."
if ! compose_cmd up -d; then
    echo "ERROR: 'docker compose up' failed." >&2
    exit 1
fi

if [ "${TEST_REQUESTED}" = true ]; then
    if wait_for_app "${PORT}" 36 5; then
        echo ""
        echo "✓ STARTUP TEST PASSED — app is up at http://127.0.0.1:${PORT}"
        print_success "${PORT}"
        exit 0
    else
        echo ""
        echo "✗ STARTUP TEST FAILED" >&2
        exit 1
    fi
fi

# Normal start: bounded best-effort wait, then report.
if ! wait_for_app "${PORT}" 12 5; then
    echo "The stack is up but the app did not become ready in time." >&2
    echo "Check the logs with: ${COMPOSE_CMD} logs -f" >&2
    exit 1
fi

print_success "${PORT}"
