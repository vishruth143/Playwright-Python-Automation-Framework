# AGENTS.md — AI Agent Guide for Playwright-Python-Automation-Framework

## Architecture Overview

Three test suites, each self-contained under `tests/`:

| Suite | Marker | Config prefix | Test root |
|---|---|---|---|
| PTA UI | `pta` | `pta_ui_*` | `tests/ui/pta/` |
| Heroku UI | `heroku` | `heroku_ui_*` | `tests/ui/heroku/` |
| JSONPlaceholder API | `jsonplaceholder` | `jsonplaceholder_api_*` | `tests/api/jsonplaceholder/` |

Each suite has its own `conftest.py` that auto-loads configuration — **no `APP_NAME`/`SERVICE_NAME` env vars needed**.

## Key Directories

- `framework/pages/ui/base_page.py` — `BasePage`: wrap all Playwright `page.*` calls here; page objects extend this. Timeouts are in **milliseconds** (default `10_000`).
- `framework/interfaces/api_client.py` — Thin wrapper around Playwright `APIRequestContext` for API tests.
- `framework/utilities/` — `custom_logger.py` (rotating log + colored console), `loaders.py` (YAML/JSON/Excel), `screenshot_utils.py`.
- `config/config_parser.py` — Single `ConfigParser` class; all config file paths are registered in `CONFIG_FILE_PATHS`. Add new configs here first.
- `tests/ui/conftest.py` — Defines `browser_context` and `page` fixtures, screenshot-on-failure hook, and video/trace capture (kept only on failure).
- `tests/conftest.py` — Session-scoped: cleans `output/` at start, writes Allure `environment.properties` and `executor.json`.

## Page Object Pattern

All page objects live under the suite's `pages/` subfolder (e.g. `tests/ui/pta/pages/`), extend `BasePage`, and accept `page: Page` in `__init__`. Use CSS selectors by default; XPath strings starting with `//` are auto-prefixed by `BasePage._locator()`.

```python
class LoginPage(BasePage):
    _USERNAME = "#username"
    def enter_username(self, value: str):
        self.type_text(self._USERNAME, value)
```

## Configuration Flow

1. `REGION` env var (default `QA`) selects the environment block inside each `*_env_config.yml`.
2. `ConfigParser.load_config('pta_ui_test_env_config')` returns the full YAML as a dict.
3. Excel data loaded via `ConfigParser.load_xlsx('pta_ui_test_excel_data_config', sheet_name)` → returns a pandas `DataFrame`.

## Running Tests (PowerShell)

```powershell
# Set env vars (optional — all have defaults)
$env:REGION="QA"; $env:BROWSER="CHROME"; $env:HEADLESS="N"

# PTA UI
pytest -vvv -m "pta" -n 4 --reruns 3 --html=output/reports/report.html --self-contained-html --alluredir=output/allure-results --capture=tee-sys --durations=10 tests

# Heroku UI
pytest -vvv -m "heroku" --reruns 3 --html=output/reports/report.html --self-contained-html --alluredir=output/allure-results --capture=tee-sys --durations=10 tests

# JSONPlaceholder API
pytest -vvv -m "jsonplaceholder" -n 4 --reruns 3 --html=output/reports/report.html --self-contained-html --alluredir=output/allure-results --capture=tee-sys --durations=10 tests

# One-click Windows executors (run > generate Allure > serve)
cmd /c executor\pta_ui_tests_executor.bat
```

## Logging

Use the `log` fixture (function-scoped, pre-stamped with worker-id and test-name) in tests:

```python
def test_example(page, log):
    log.info("navigating to home page")
```

xdist workers write separate shard files (`test_execution_gw0.log`, …); they are merged into `output/logs/test_execution.log` after the session ends.

## Output Artifacts

`output/` is **deleted and recreated** at the start of every test session (controller process only). Never store anything you need to keep inside `output/`.

| Path | Contents |
|---|---|
| `output/logs/test_execution.log` | Merged rotating log (10 MB / 5 backups) |
| `output/screenshots/` | PNG captured on failure |
| `output/videos/` | WebM + trace ZIP kept only for failed tests |
| `output/allure-results/` | Raw Allure JSON results |
| `output/reports/` | pytest-html self-contained HTML |

## Adding a New Test Suite

1. Create `tests/<type>/<app>/` with `__init__.py`, `conftest.py`, `test_<app>.py`, and `pages/`.
2. Add a new marker to `pytest.ini`.
3. Register new config files in `config/config_parser.py` → `CONFIG_FILE_PATHS`.
4. Add config files under `config/<type>/<app>/`.
5. Add an executor script under `executor/` if needed.

## Conventions

- Commits follow **Conventional Commits**: `feat(pta):`, `fix(conftest):`, `chore(deps):`, etc.
- `BROWSER` env var accepts `CHROME`, `FIREFOX`, `EDGE`; `HEADLESS` accepts `Y`/`N`.
- Parallel execution (`-n 4`) is safe for UI and API suites; Heroku tests omit `-n` by default.
- `pylint` is configured via inline `# pylint: disable=` comments at the top of each file — follow the same pattern when adding files.

