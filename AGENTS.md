# Repository Guidelines

## Project Structure & Module Organization
- `libchickadee/` is the primary source package. Key submodules live under `libchickadee/parsers/` and `libchickadee/resolvers/`.
- `libchickadee/test/` contains unit tests and fixtures (for example `vt_resp_data.json`).
- `doc_src/` holds Sphinx sources; generated HTML is in `docs/`.
  - Do not spend time reviewing `docs/`, as it is generated from `doc_src/` and should not be edited directly.

## Build, Test, and Development Commands
- `uv sync` installs dependencies (the `dev` group includes docs tooling).
- `uv run chickadee --help` runs the CLI entry point defined in `[project.scripts]`.
- `uvx pre-commit run --all-files` runs formatting, linting, and type checks.
- `uv run pytest --cov --cov-branch --cov-fail-under 85` runs tests with coverage.
- `cd doc_src && uv run make html` builds documentation only (uses the Sphinx Makefile).

## Coding Style & Naming Conventions
- Python code lives under `libchickadee/`; keep module names lowercase with underscores (for example `plain_text.py`).
- Follow PEP 8 conventions and keep linting clean with `ruff` (see `pyproject.toml`).
- Keep test names descriptive and aligned to functionality (for example `test_resolver_ipapi.py`).

## Testing Guidelines
- Tests are under `libchickadee/test/` and run with `pytest` (see CI).
- Keep tests focused on parser and resolver behavior; include fixtures under `libchickadee/test/` when needed.

## Commit & Pull Request Guidelines
- Keep commits tiny — one logical change per commit. Small commits make review easier and keep `git bisect` useful.
- Each commit message must have a single-letter prefix followed by ` - ` and a brief one-sentence description of **why** the change was made.

| Prefix | Meaning |
|--------|-------------------------------|
| F      | Feature                       |
| B      | Bug fix                       |
| t      | Test-only change              |
| d      | Documentation-only change     |
| a      | Automated formatting change   |
| R      | Refactor                      |

- If a commit could reasonably carry more than one prefix, the commit is too large — break it into smaller commits before saving.
- PRs should include a clear description of the change, any relevant issue links, and updates to docs/tests when behavior changes.

## Security & Configuration Tips
- Review `SECURITY.md` for vulnerability reporting.
- Resolver credentials and runtime options are typically configured via `template_chickadee.ini`; avoid committing real API keys.
- If using the devcontainer, report any failure to connect to a domain or website, so that the allow list can be updated & reloaded to permit access.
