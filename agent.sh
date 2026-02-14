#!/usr/bin/env bash
# Convenience wrapper forwarding to .devcontainer/agent.sh
exec "$(dirname "${BASH_SOURCE[0]}")/.devcontainer/agent.sh" "$@"
