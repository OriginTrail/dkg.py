# AGENTS.md

Guide for agentic coding assistants in `dkg.py`.

## 1) Repo Context
- Python SDK for OriginTrail DKG.
- Python version: `^3.10` in `pyproject.toml`; local pin is `3.11.11` in `.python-version`.
- Tooling: Poetry, Ruff, Pytest, pre-commit.
- Main package is `dkg/`; tests live in `test/`.
- CI facts:
  - `.github/workflows/checks.yml` runs `poetry run make run-test`.
  - `.github/workflows/ruff.yml` runs Ruff on pull requests.

## 2) Setup
Run from repository root.

```bash
poetry install
pre-commit install
```

Equivalent helper target:

```bash
make install
```

## 3) Build / Lint / Test Commands
Use these as canonical commands.

```bash
# Build
poetry build

# Lint + format (preferred)
make ruff

# Same as make ruff
poetry run ruff check --fix
poetry run ruff format

# Tests (all)
make run-test
# Same as make run-test
poetry run pytest

# Optional: run pre-commit hooks on all files
poetry run pre-commit run --all-files
```

## 4) Single-Test Commands (Important)
When iterating, run the smallest relevant scope first.

```bash
# Single file
poetry run pytest test/knowledge_collection_tools_test.py

# Single class
poetry run pytest test/knowledge_collection_tools_test.py::TestGroupNQuadsBySubject

# Single test
poetry run pytest test/knowledge_collection_tools_test.py::TestGroupNQuadsBySubject::test_resource_object_quad

# Name filter
poetry run pytest -k "blank_node_replacement"
```

## 5) Test Discovery Rules
From `pyproject.toml`:

- `testpaths = ["test"]`
- accepted file patterns:
  - `test_*.py`
  - `*_test.py`

## 6) Formatting and General Style
- Follow Ruff formatter output; do not hand-style against it.
- Keep code PEP 8 compliant and formatter-friendly.
- Prefer small focused functions over deeply nested logic.
- Use trailing commas in multiline literals/calls when formatter expects them.
- Preserve the Apache license header pattern for new modules in `dkg/`.

## 7) Import Conventions
- Group imports with blank lines in this order:
  1. standard library
  2. third-party
  3. local `dkg` imports
- Prefer explicit imports; avoid wildcard imports.
- Re-exporting in package `__init__.py` may use existing `# NOQA: F401` style.
- Use `TYPE_CHECKING` imports when needed to avoid runtime cycles.

## 8) Typing Conventions
- Add type hints for all new/changed public APIs.
- Prefer modern annotations: `dict[str, Any]`, `list[str]`, and `A | B`.
- Reuse domain aliases from `dkg.types` (`UAL`, `Address`, `ChecksumAddress`, `Wei`, etc.).
- Use dataclasses, `TypedDict`, and `NamedTuple` for structured payloads.
- Keep sync/async signatures aligned across paired modules.

## 9) Naming Conventions
- files/modules: `snake_case.py`
- classes: `PascalCase`
- methods/functions/variables: `snake_case`
- constants and enum values: `UPPER_SNAKE_CASE`
- internal helper/bound methods: leading underscore (`_get`, `_query`, `_attach_modules`)
- preserve external protocol field naming:
  - snake_case on Python method inputs
  - camelCase in request schema keys where external APIs/contracts require it.

## 10) Error Handling Conventions
- Prefer custom exceptions from `dkg.exceptions`.
- Raise specific exception types with actionable messages.
- Catch broad exceptions only at IO/network/provider boundaries, then wrap.
- Do not silently swallow errors; propagate or map to structured failure output.
- Keep operation payloads consistent (`status`, `data`, `operationId`).
- Keep retries explicit and bounded (`max_retries`, `frequency`, backoff/retry helpers).

## 11) Architecture Patterns to Preserve
- Request schema objects belong in:
  - `dkg/utils/blockchain_request.py`
  - `dkg/utils/node_request.py`
- Method descriptor pattern:
  - private binding: `_method = Method(...)`
  - public wrapper: normalize inputs and orchestrate calls.
- Maintain sync/async behavior parity:
  - `dkg/clients/dkg.py`
  - `dkg/clients/async_dkg.py`
- Use `InputService` for option default resolution; avoid duplicating fallback logic.
- Keep UAL parsing/formatting in `dkg.utils.ual`.

## 12) Agent Workflow Expectations
- Keep diffs minimal and targeted.
- After edits, run:
  1. `poetry run ruff check --fix`
  2. `poetry run ruff format`
  3. focused pytest scope, then broader tests as needed
- Add/update tests for behavior changes.
- Update docs/examples when user-facing behavior changes.
- Never hardcode secrets; `.env` is local and ignored.

## 13) Cursor and Copilot Rules
Repository scan result:

- No `.cursorrules` file.
- No `.cursor/rules/` directory.
- No `.github/copilot-instructions.md` file.

If these files are added later, treat them as high-priority repo instructions and update this guide.

## 14) Notes
- Makefile demo targets are `demo`, `async-demo`, and `paranet-demo`.
- Prefer `poetry run ...` for deterministic local execution.
