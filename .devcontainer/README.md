# Devcontainer

This directory defines a containerized development environment for running
Claude Code (or any interactive shell) with network egress locked down to an
explicit domain allowlist. It works two ways:

- **VS Code / DevPod** — open the repo in any editor that supports the
  [Dev Containers spec](https://containers.dev) and the workspace container
  starts automatically.
- **Headless via `agent.sh`** — run `./agent.sh help` from a terminal to see
  available commands. This is the quickest way to launch Claude Code without an
  IDE: `./agent.sh claude` drops you straight into a sandboxed session.

## How it works

`docker-compose.yaml` brings up two services:

| Service | Role |
|---------|------|
| **workspace** | Node 20 container with Claude Code, `uv`, zsh, and common dev tools. All HTTP(S) traffic is routed through the proxy. |
| **egress-proxy** | Squid forward-proxy that only allows CONNECT/HTTP to domains listed in the allowlist. |

The workspace container sits on an internal-only Docker network and cannot
reach the internet directly — every outbound request must pass through the
proxy, which checks it against the merged allowlist.

## Managing allowed domains

The proxy allowlist is assembled from two files under `squid/`:

| File | Purpose |
|------|---------|
| `allowed_domains.txt` | Checked into git — shared across the team. |
| `allowed_domains.local.txt` | Git-ignored — personal overrides that stay on your machine. |

At startup (and on every `proxy-add` / `proxy-reload`) the two files are
merged, deduplicated, and mounted into the proxy container. Use `agent.sh
proxy-add` and `agent.sh proxy-remove` to edit these lists without touching
files by hand.

## Resource limits

The workspace container defaults to 4 GB RAM, 2 CPUs, and 1024 PIDs. Adjust
these in `docker-compose.yaml` if your workload needs more headroom.
