# Contributing Guide

Thank you for helping improve Machine Theory of Mind! This document outlines how to get
set up, propose changes, and keep the codebase healthy.

## Development setup
1. **Clone & install dependencies**
   ```bash
   git clone https://github.com/dyra-12/Machine-Theory-Of-Mind.git
   cd Machine-Theory-Of-Mind
   python -m venv .venv && source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. **Optional containers**: Build/run the Docker image with `make docker-build` and
   `make docker-shell` (see `Makefile`).

## Workflow
1. Fork the repo and create a feature branch (`git checkout -b feature/my-change`).
2. Make focused commits with descriptive messages.
3. Run quality gates before pushing:
   ```bash
   make lint
   make test
   ```
4. Open a pull request describing the motivation, changes, and testing done. Reference any
   linked issues and update docs/tests as needed.

## Design & code style
- Prefer type hints and docstrings for public APIs.
- Keep modules small and cohesive; favor composition over giant classes.
- Follow the formatting enforced by `black` and lint fixes suggested by `ruff`.
- Document new configuration flags in `README.md` or the relevant `docs/` page.

## Tests
- Place fast unit tests under `tests/` and ensure they pass via `pytest -q`.
- For experiments, provide deterministic seeds or mock data so CI can run quickly.

## Reporting issues & discussions
- Use GitHub Issues for bugs or feature requests, including minimal reproduction steps.
- Start design discussions via GitHub Discussions or PR drafts when architectural changes
  are needed.

By contributing, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
