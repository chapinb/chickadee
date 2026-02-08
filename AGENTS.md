# Repository Guidelines

## Project Structure & Module Organization
- `libchickadee/` is the primary source package. Key submodules live under `libchickadee/parsers/` and `libchickadee/resolvers/`.
- `libchickadee/test/` contains unit tests and fixtures (for example `vt_resp_data.json`).
- `doc_src/` holds Sphinx sources; generated HTML is in `docs/`.
  - Do not spend time reviewing `docs/`, as it is generated from `doc_src/` and should not be edited directly.

## Build, Test, and Development Commands
- `uv sync --group test --group docs` installs dependency groups from `pyproject.toml`.
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
- Recent history shows short, imperative commit messages (for example `Bump urllib3 from 2.0.2 to 2.0.6`). Match that style.
- PRs should include a clear description of the change, any relevant issue links, and updates to docs/tests when behavior changes.

## Security & Configuration Tips
- Review `SECURITY.md` for vulnerability reporting.
- Resolver credentials and runtime options are typically configured via `template_chickadee.ini`; avoid committing real API keys.
