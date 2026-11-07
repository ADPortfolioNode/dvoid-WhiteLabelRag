#!/usr/bin/env bash
# Silo-safe host-port resolution for WhiteLabelRag.
#
# Rule (same as the other projects): each repo is a silo.
# - A port held by OUR OWN container (name/image containing
#   "whitelabel-rag") is freed by stopping that container; we keep
#   the original host port.
# - A port held by anything else (another app's container, or a host
#   process) is never freed: the host port bumps +1, retrying up to
#   10 steps from the preferred port.
# Container ports never change; only the host side of the mapping
# moves. The resolved value is exported in the variable named by
# the caller, which must match the variable the compose file reads
# (PORT for the app service).

WLR_OWN_MATCH="whitelabel-rag"

host_port_in_use() {
    local port="$1"

    if command -v docker >/dev/null 2>&1; then
        if docker ps --format '{{.Ports}}' 2>/dev/null | grep -qE "(0\\.0\\.0\\.0|127\\.0\\.0\\.1|:::|\\[::\\]):${port}->"; then
            return 0
        fi
    fi

    case "$(uname -s 2>/dev/null || echo unknown)" in
        MINGW*|MSYS*|CYGWIN*)
            if command -v powershell.exe >/dev/null 2>&1; then
                powershell.exe -NoProfile -Command \
                    "if (Get-NetTCPConnection -LocalPort ${port} -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1) { exit 0 } else { exit 1 }" \
                    >/dev/null 2>&1
                return $?
            fi
            ;;
    esac

    if command -v ss >/dev/null 2>&1; then
        ss -ltn 2>/dev/null | grep -qE ":${port}[[:space:]]"
        return $?
    fi

    if command -v netstat >/dev/null 2>&1; then
        netstat -ltn 2>/dev/null | grep -qE ":${port}[[:space:]]"
        return $?
    fi

    return 1
}

# Print "name|image" of the container publishing host $1, or nothing.
port_holder_container() {
    local port="$1"
    local ps_out name image ports
    ps_out=$(docker ps --format '{{.Names}}|{{.Image}}|{{.Ports}}' 2>/dev/null || true)
    while IFS='|' read -r name image ports; do
        case "$ports" in
            *"0.0.0.0:${port}->"*|*"127.0.0.1:${port}->"*|*":::${port}->"*|*"[::]:${port}->"*)
                printf '%s|%s' "$name" "$image"
                return 0
                ;;
        esac
    done <<EOF
$ps_out
EOF
    return 1
}

is_own_holder() {
    local name="$1" image="$2"
    case "${name}|${image}" in
        *"${WLR_OWN_MATCH}"*) return 0 ;;
    esac
    return 1
}

# Resolve one host port into $1 (starting at $2, or the current value
# of $1 when already set, e.g. from .env). Exports the resolved value.
resolve_compose_host_port() {
    local var_name="$1" preferred="$2"
    local port="${!var_name:-$preferred}"
    local tries=0

    while [ "$tries" -le 10 ]; do
        if ! host_port_in_use "$port"; then
            export "${var_name}=${port}"
            return 0
        fi

        local holder hname himage
        if holder=$(port_holder_container "$port") && [ -n "$holder" ]; then
            hname="${holder%%|*}"
            himage="${holder#*|}"
            if is_own_holder "$hname" "$himage"; then
                echo "Port ${port} is held by our own container ${hname}; stopping it and keeping port ${port}." >&2
                docker rm -f "$hname" >/dev/null 2>&1 || true
                if ! host_port_in_use "$port"; then
                    export "${var_name}=${port}"
                    return 0
                fi
                echo "Port ${port} is still busy after stopping ${hname}; bumping." >&2
            else
                echo "Port ${port} is held by unrelated container ${hname}; bumping to $((port + 1))." >&2
            fi
        else
            echo "Port ${port} is held by another process (not a container); bumping to $((port + 1))." >&2
        fi
        port=$((port + 1))
        tries=$((tries + 1))
    done

    echo "ERROR: Could not find a free host port near ${preferred} for ${var_name} (tried 10 bumps)." >&2
    return 1
}

resolve_compose_host_ports() {
    resolve_compose_host_port PORT 5000 || return 1
    return 0
}
