# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Run Tests
```bash
# Run all tests (by marker)
pytest -vvv -m "pta" -n 4 --reruns 3 --html=output/reports/report.html --self-contained-html --alluredir=output/allure-results --capture=tee-sys tests
pytest -vvv -m "heroku" --reruns 3 --html=output/reports/report.html --self-contained-html --alluredir=output/allure-results tests
pytest -vvv -m "jsonplaceholder" -n 4 --reruns 3 --html=output/reports/report.html --self-contained-html --alluredir=output/allure-results tests

# Run a single test
pytest -vvv tests/ui/heroku/test_heroku.py::TestHeroku::test_login

# Set env vars (PowerShell)
$env:REGION="QA"; $env:BROWSER="CHROME"; $env:HEADLESS="N"
```

### Lint
```bash
pylint tests          # CI enforces score = 10.0/10
pylint framework
```

### Generate and View Allure Report
```bash
allure generate output/allure-results --clean -o output/allure-report
python -m http.server 8000   # open http://localhost:8000/output/allure-report
```

### Docker
```bash
docker build -t playwright-python-automation .
docker run -e REGION=qa -e BROWSER=CHROME -e HEADLESS=Y playwright-python-automation
```

## Architecture

### Layers

```
config/            → YAML/JSON/Excel test data + env configs, registered in config_parser.py
framework/
  interfaces/      → APIClient: thin Playwright APIRequestContext wrapper
  pages/ui/        → BasePage: all Playwright interactions; all page objects extend this
  utilities/       → Logger, loaders, helpers, screenshot capture
tests/
  conftest.py      → Session hooks: clean output/, write Allure metadata, merge log shards
  ui/conftest.py   → browser_context + page fixtures, screenshot-on-failure hook
  ui/<suite>/      → Suite-specific page objects, conftest (testdata fixture), test files
  api/<suite>/     → Suite-specific conftest (api_client + testdata fixtures), test files
```

### Configuration Flow

`config/config_parser.py` holds `CONFIG_FILE_PATHS` — a dict mapping config names to paths. All new config files must be registered here. Tests load config via `ConfigParser.load_config(name)` (YAML/JSON) or `ConfigParser.load_xlsx(name, sheet_name)` (Excel).

Active environment is controlled by env vars:
- `REGION` → QA / DEV / STAGE / PROD (default: QA)
- `BROWSER` → CHROME / FIREFOX / EDGE (default: CHROME)
- `HEADLESS` → Y / N (default: N locally, Y in CI)

Config YAMLs are keyed by region name at the top level.

### Fixture Hierarchy (UI)

```
tests/conftest.py            session  – cleanup, Allure setup
tests/ui/conftest.py         function – page, browser_context, region, log
tests/ui/<suite>/conftest.py session  – testdata (suite-specific config)
```

The `log` fixture yields a logger pre-stamped with `worker_id` and `test_name` — use it in every test for parallel-safe output. The `browser_context` fixture captures video + traces and keeps them only on failure.

### BasePage

All page objects extend `BasePage(page: Page, timeout: int = 10_000)` in `framework/pages/ui/base_page.py`. Timeouts are in **milliseconds**. Locators starting with `//` are auto-prefixed as `xpath=`; everything else is treated as CSS.

Conventions:
- Locator constants are private: `_USERNAME = "#username"`
- Each public method wraps one user action: `enter_username(value)`, `click_submit()`

### APIClient

`framework/interfaces/api_client.py` wraps `APIRequestContext`. Returns a `_PlaywrightResponse` with `.status_code`, `.text`, `.json()`, `.headers`.

### Logger

`framework/utilities/custom_logger.py` is xdist-aware: each worker writes to a shard file (`test_execution_gw0.log`, etc.), shards are merged to `output/logs/test_execution.log` at session end.

## Adding a New Test Suite

1. Create `tests/<type>/<app>/` with `__init__.py`, `conftest.py` (testdata fixture), `test_<app>.py`, and `pages/` (UI only).
2. Register a marker in `pytest.ini`.
3. Add config files under `config/<type>/<app>/` and register them in `config/config_parser.py → CONFIG_FILE_PATHS`.
4. Optionally add an executor batch script under `executor/`.

## Code Quality

Pylint must score **10.0/10** — CI blocks merges below this. Silence expected warnings with per-file `# pylint: disable=[...]` at the top. Do not suppress warnings globally.

## Commit Convention

`<type>(<scope>): <message>`

Types: `feat`, `fix`, `chore`, `test`, `docs`, `refactor`, `ci`, `style`, `perf`  
Common scopes: `deps`, `conftest`, `logger`, `common`, `config`, `pta`, `heroku`, `jsonplaceholder`, `ci`

## CI

`.github/workflows/ci.yml` runs on push/PR (when `config/`, `framework/`, `tests/`, or `pytest.ini` change) and on a daily schedule (03:30 UTC).

1. **lint** – `pylint tests` on ubuntu, must be 10.0/10
2. **build-and-test** (depends on lint) – runs `pytest -m "pta or heroku" -n 4`, uploads `allure-report.zip` as artifact