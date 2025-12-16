# Repository Guidelines

## Project Structure & Module Organization

Core runtime code lives in `videomorph/`: `main.py` bootstraps the PyQt6 GUI, `converter.py` coordinates ffmpeg invocations, and helpers such as `profiles.py`, `task.py`, `media.py`, `vmpath.py`, and `utils.py` match the modules exercised under `tests/`. Qt Designer sources and icons stay in `ui/` and `qrc/`; update these and regenerate the compiled resources inside `videomorph/forms/` instead of editing generated files. Packaging scripts (`bin/`, `videomorph_deb/`) should only change when cutting releases, and remember that VideoMorph now targets the system-provided ffmpeg binaries instead of bundling its own copies. Shared assets (docs, i18n bundles, manuals, sounds) all resolve through `videomorph/converter/vmpath.py`, so new code should request files via those helpers instead of manually building paths.

## Build, Test, and Development Commands

- `uv venv` – create the project’s `.venv` using the Python pinned in `pyproject.toml`.
- `source .venv/bin/activate` (or `.\.venv\Scripts\activate`) followed by `uv sync --group dev` – install runtime and dev dependencies from `uv.lock`.
- `uv run ./bin/videomorph` (or `uv run python videomorph/main.py`) – launch the GUI against local sources.
- `uv run pytest` / `uv run pytest tests/test_converter.py -k profile` – execute the full suite or a focused subset.
- `uv run pytest --cov=videomorph --cov-report=xml` – refresh `coverage.xml` before sharing artifacts.

## Coding Style & Naming Conventions

Follow PEP8 (4-space indents, 100-char soft limit) and describe public APIs with concise PEP257 docstrings. Use snake_case for functions, PascalCase for PyQt widgets, and align resource identifiers with their `.ui` counterparts. Keep module names descriptive (`vmpath`, `profiles`) and mirror them in test filenames. Favor explicit type hints for new functions, use `pathlib.Path` (never `os.path`) for every filesystem operation, and run `uv run pylint` or `uv run flake8` before opening a PR.

## Testing Guidelines

The suite relies on `pytest` plus `pytest-qt`; prefer deterministic tests that stub ffmpeg paths via `videomorph.vmpath`. Name tests after observed behavior (`test_profiles_loads_defaults`) and keep fixtures in `tests/conftest.py` if shared. GUI changes must include at least one assertion around emitted signals or widget state. Maintain or improve the coverage recorded in `coverage.xml` and mention any manual media conversions performed. Store new golden assets under `tests/resources/` and load them via `Path(__file__).parent`.

## Commit & Pull Request Guidelines

Work on feature branches named `username_i123_topic`. Commit subjects stay within 50 chars, use the imperative mood, and include a blank line before any wrapped body text (≤72 chars) explaining what and why. PRs target `develop`, reference the issue number, summarize automated (`uv run pytest`, coverage) and manual checks, and attach screenshots or screencasts for visual tweaks. Update docs, presets, and resource files alongside code so reviewers can exercise the same flow.

## Configuration Overrides

- User-specific data lives under `~/.videomorph`: Qt state sits in `config.ini`, and editable conversion presets are copied into `~/.videomorph/profiles`.
- Advanced users can extend `~/.videomorph/paths.ini` using `[paths]` entries (e.g. `doc=/opt/share/videomorph/doc`) or `[tools]` entries (`ffmpeg=/usr/local/bin/ffmpeg`, `ffprobe=...`) to override resource directories or binary locations without patching the codebase.
- Always prefer the helpers exposed by `videomorph/converter/vmpath.py` (`resource_path`, `manual_path`, `sound_file`, `settings_file`) when reading or writing files so these overrides are honored automatically.
