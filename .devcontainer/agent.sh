#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# agent.sh — CLI for agentic development without VS Code
#
# Usage:  ./agent.sh <command> [args]
# Run ./agent.sh help for details.
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yaml"
PROJECT_NAME="devcontainer"

COMMITTED_DOMAINS="$SCRIPT_DIR/squid/allowed_domains.txt"
LOCAL_DOMAINS="$SCRIPT_DIR/squid/allowed_domains.local.txt"
RUNTIME_DIR="$SCRIPT_DIR/runtime"
MERGED_DOMAINS="$RUNTIME_DIR/allowed_domains.txt"

# --- Container runtime detection -------------------------------------------

detect_compose() {
    if docker compose version &>/dev/null; then
        echo "docker compose"
    elif command -v podman-compose &>/dev/null; then
        echo "podman-compose"
    elif command -v docker-compose &>/dev/null; then
        echo "docker-compose"
    else
        echo >&2 "Error: No container compose tool found."
        echo >&2 "Install one of: docker compose v2, podman-compose, docker-compose v1"
        exit 1
    fi
}

COMPOSE="$(detect_compose)"

compose() {
    # shellcheck disable=SC2086
    $COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" "$@"
}

# --- Domain merge -----------------------------------------------------------

merge_domains() {
    mkdir -p "$RUNTIME_DIR"
    {
        # Strip comments and blank lines from committed list
        if [[ -f "$COMMITTED_DOMAINS" ]]; then
            grep -v '^\s*#' "$COMMITTED_DOMAINS" | grep -v '^\s*$'
        fi
        # Strip comments and blank lines from local overrides
        if [[ -f "$LOCAL_DOMAINS" ]]; then
            grep -v '^\s*#' "$LOCAL_DOMAINS" | grep -v '^\s*$'
        fi
    } | sort -u > "$MERGED_DOMAINS"
}

# --- Proxy helpers ----------------------------------------------------------

proxy_is_running() {
    compose ps --status running 2>/dev/null | grep -q egress-proxy
}

proxy_reload_if_running() {
    if proxy_is_running; then
        compose exec egress-proxy squid -k reconfigure
    fi
}

# --- Commands ---------------------------------------------------------------

cmd_claude() {
    merge_domains
    compose run --rm workspace claude "$@"
}

cmd_shell() {
    merge_domains
    compose run --rm workspace zsh
}

cmd_build() {
    compose build workspace
}

cmd_down() {
    compose down
}

cmd_status() {
    compose ps
}

cmd_logs() {
    compose logs "$@"
}

cmd_proxy_add() {
    local domain=""
    local local_flag=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --local) local_flag=true; shift ;;
            -*) echo >&2 "Unknown flag: $1"; exit 1 ;;
            *) domain="$1"; shift ;;
        esac
    done

    if [[ -z "$domain" ]]; then
        echo >&2 "Usage: agent.sh proxy-add <domain> [--local]"
        exit 1
    fi

    local target
    if $local_flag; then
        target="$LOCAL_DOMAINS"
    else
        target="$COMMITTED_DOMAINS"
    fi

    # Append if not already present
    if ! grep -qxF "$domain" "$target" 2>/dev/null; then
        echo "$domain" >> "$target"
        echo "Added $domain to $(basename "$target")"
    else
        echo "$domain already in $(basename "$target")"
    fi

    merge_domains
    proxy_reload_if_running
}

cmd_proxy_remove() {
    local domain="${1:-}"
    if [[ -z "$domain" ]]; then
        echo >&2 "Usage: agent.sh proxy-remove <domain>"
        exit 1
    fi

    if [[ -f "$LOCAL_DOMAINS" ]]; then
        local tmp
        tmp=$(mktemp)
        grep -vxF "$domain" "$LOCAL_DOMAINS" > "$tmp" || true
        mv "$tmp" "$LOCAL_DOMAINS"
        echo "Removed $domain from local overrides"
    fi

    if grep -qxF "$domain" "$COMMITTED_DOMAINS" 2>/dev/null; then
        echo "Note: $domain is also in the committed allowlist ($(basename "$COMMITTED_DOMAINS"))."
        echo "Edit that file directly to remove it for the whole team."
    fi

    merge_domains
    proxy_reload_if_running
}

cmd_proxy_list() {
    merge_domains
    if [[ -s "$MERGED_DOMAINS" ]]; then
        cat "$MERGED_DOMAINS"
    else
        echo "(empty — no domains in allowlist)"
    fi
}

cmd_proxy_reload() {
    merge_domains
    if proxy_is_running; then
        compose exec egress-proxy squid -k reconfigure
        echo "Proxy configuration reloaded"
    else
        echo "Proxy is not running"
    fi
}

cmd_help() {
    cat <<'EOF'
Usage: agent.sh <command> [args]

Commands:
  claude [args]            Run claude in an ephemeral workspace container
  shell                    Start an interactive zsh session in the workspace
  build                    Build the workspace image
  down                     Stop all containers
  status                   Show container status
  logs [args]              Show container logs

  proxy-add <domain> [--local]
                           Add domain to the allowlist (default: committed file;
                           --local for personal overrides not checked into git)
  proxy-remove <domain>    Remove domain from local overrides
  proxy-list               Show the effective merged allowlist
  proxy-reload             Merge domains and reconfigure the running proxy

  help                     Show this help message

Examples:
  ./agent.sh build
  ./agent.sh claude -- --help
  ./agent.sh shell
  ./agent.sh proxy-add .example.com --local
  ./agent.sh down
EOF
}

# --- Main -------------------------------------------------------------------

command="${1:-help}"
shift || true

case "$command" in
    claude)       cmd_claude "$@" ;;
    shell)        cmd_shell ;;
    build)        cmd_build ;;
    down)         cmd_down ;;
    status)       cmd_status ;;
    logs)         cmd_logs "$@" ;;
    proxy-add)    cmd_proxy_add "$@" ;;
    proxy-remove) cmd_proxy_remove "$@" ;;
    proxy-list)   cmd_proxy_list ;;
    proxy-reload) cmd_proxy_reload ;;
    help|--help|-h) cmd_help ;;
    *)
        echo >&2 "Unknown command: $command"
        echo >&2 "Run '$0 help' for usage."
        exit 1
        ;;
esac
