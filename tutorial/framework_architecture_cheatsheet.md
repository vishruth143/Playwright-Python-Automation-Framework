# 🗂️ Automation Framework — Architecture Cheatsheet
> **Quick Reference for Interview Prep | Built from Scratch | Python + Playwright**

---

## ⚡ Elevator Pitch (30 sec)
> *"Multi-layer automation framework built from scratch in Python using Playwright as the core engine.
> Covers UI · API · Mobile · Performance — unified structure, shared config, parallel execution, Allure reporting."*

---

## 📐 Project Structure at a Glance

```
Playwright-Python-Automation-Framework/
│
├── config/                         ← All env + test data configs (YAML/JSON/Excel)
│   ├── config_parser.py            ← Central registry — ALL configs registered here
│   ├── ui/pta/  ui/heroku/         ← UI suite configs
│   ├── api/jsonplaceholder/        ← API suite configs
│   ├── mobile/kwa/  mobile/wdio/   ← Mobile suite configs
│   └── performance/jsonplaceholder/← Performance configs
│
├── framework/                      ← Reusable core (not test code)
│   ├── pages/ui/base_page.py       ← BasePage — ALL Playwright UI calls go here
│   ├── interfaces/api_client.py    ← APIClient — thin Playwright HTTP wrapper
│   ├── utilities/
│   │   ├── custom_logger.py        ← xdist-aware parallel logger
│   │   ├── loaders.py              ← YAML / JSON / Excel file loaders
│   │   ├── screenshot_utils.py     ← Failure screenshot capture
│   │   ├── emulator_launcher.py    ← Android ADB boot detection
│   │   └── common.py               ← Faker data gen, Excel helpers, login utils
│   └── listeners/event_listeners.py← Browser event hooks
│
├── tests/
│   ├── conftest.py                 ← SESSION: clean output/, Allure setup, log merge
│   ├── ui/
│   │   ├── conftest.py             ← FUNCTION: browser, video/trace, screenshot-on-fail
│   │   ├── heroku/                 ← Heroku UI test suite
│   │   └── pta/                    ← PTA UI test suite (Excel data-driven)
│   ├── api/
│   │   └── jsonplaceholder/        ← Full CRUD API test suite
│   ├── mobile/
│   │   ├── kwa/                    ← KWA Android app tests
│   │   └── wdio/                   ← WDIO demo app tests
│   └── performance/
│       └── locustfile.py           ← Locust load test tasks
│
├── executor/                       ← One-click .bat runners (local + CI)
└── output/                         ← Auto-cleaned each run (logs/screenshots/reports)
```

---

## 🧱 The 4 Testing Layers

### 1️⃣ UI Layer — Playwright + Page Object Model

| What | How |
|---|---|
| Engine | Playwright sync API |
| Base class | `BasePage` in `framework/pages/ui/base_page.py` |
| Page objects | Extend `BasePage`, define locator constants + business methods |
| Locators | CSS by default; strings starting with `//` → auto `xpath=` prefix |
| Timeout | 10,000 ms (centralized, no magic numbers in tests) |
| Suites | **Heroku** (auth, forms, drag-drop) · **PTA** (Excel data-driven) |

```python
# Page Object pattern
class LoginPage(BasePage):
    _USERNAME = "#username"           # private locator constant
    _PASSWORD = "#password"
    _SUBMIT   = "button[type='submit']"

    def enter_username(self, value: str):
        self.type_text(self._USERNAME, value)   # BasePage method
    def click_submit(self):
        self.click(self._SUBMIT)
```

```python
# Test — clean, no Playwright internals
def test_login(page, testdata, log):
    login = LoginPage(page)
    login.enter_username(testdata["username"])
    login.enter_password(testdata["password"])
    login.click_submit()
    assert login.get_text(".flash") == "You logged into a secure area!"
```

---

### 2️⃣ API Layer — Playwright APIRequestContext

| What | How |
|---|---|
| Engine | Playwright's built-in `APIRequestContext` (no `requests` lib needed) |
| Wrapper | `APIClient` in `framework/interfaces/api_client.py` |
| Verbs | GET · POST · PUT · PATCH · DELETE |
| Response | `_PlaywrightResponse` → `.status_code` · `.json()` · `.text` · `.headers` |
| Suite | **JSONPlaceholder** — full CRUD with parametrized test cases |

```python
# APIClient usage in a test
def test_get_post(api_client, testdata):
    response = api_client.get("/posts/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_post(api_client, testdata):
    payload = testdata["new_post"]
    response = api_client.post("/posts", json=payload)
    assert response.status_code == 201
```

> **Why Playwright for API?** — Single dependency, consistent response model, no extra installs.

---

### 3️⃣ Mobile Layer — Appium + Android Emulator

| What | How |
|---|---|
| Engine | Appium (WebDriver protocol) |
| Emulator | `emulator_launcher.py` — ADB boot detection, no hardcoded `sleep()` |
| Apps | **KWA** · **WDIO** (APKs stored in `framework/app_apk/`) |
| Config | Isolated per app under `config/mobile/` |

```python
# emulator_launcher.py — polls until boot is complete
def wait_for_emulator_boot():
    while True:
        result = subprocess.run(
            ["adb", "shell", "getprop", "sys.boot_completed"],
            capture_output=True, text=True
        )
        if result.stdout.strip() == "1":
            break
        time.sleep(2)
```

> **Why ADB polling?** — Eliminates flaky `time.sleep(30)` — boots fast on capable machines, waits longer on slow CI.

---

### 4️⃣ Performance Layer — Locust

| What | How |
|---|---|
| Engine | Locust (Python-native load testing) |
| Entry point | `tests/performance/locustfile.py` |
| Config | Reuses `config/performance/jsonplaceholder/` — same `REGION` env var |
| Target | JSONPlaceholder API — GET/POST load tasks |

```python
# locustfile.py snippet
class APIUser(HttpUser):
    @task(3)
    def get_posts(self):
        self.client.get("/posts")

    @task(1)
    def create_post(self):
        self.client.post("/posts", json={"title": "test", "body": "body", "userId": 1})
```

> **Key advantage:** Shares the same config system — switch `REGION=PROD` to load-test production with zero code changes.

---

## ⚙️ Cross-Cutting Concerns

### 🔧 Configuration Management

```
REGION env var  →  QA (default) | DEV | STAGE | PROD
BROWSER         →  CHROME (default) | FIREFOX | EDGE
HEADLESS        →  N (default local) | Y (CI)
```

```python
# config_parser.py — central registry
CONFIG_FILE_PATHS = {
    "pta_ui_test_env_config":    "config/ui/pta/ui_test_env_config.yml",
    "heroku_ui_test_data_config": "config/ui/heroku/ui_test_data_config.yml",
    "jsonplaceholder_api_env":   "config/api/jsonplaceholder/api_test_env_config.yml",
    # ... all configs registered here
}

# Usage in a conftest
config = ConfigParser.load_config("heroku_ui_test_env_config")
base_url = config[region]["base_url"]
```

---

### 🪵 Parallel Logging (xdist-aware)

```
pytest -n 4 runs 4 workers (gw0, gw1, gw2, gw3)
     ↓
Each worker writes → output/logs/test_execution_gw0.log
                                  test_execution_gw1.log ...
     ↓
Session teardown merges → output/logs/test_execution.log  ✅
```

```python
# log fixture — pre-stamped, use in every test
def test_login(page, log):
    log.info("Navigating to login page")   # → [gw2][test_login] Navigating to login page
```

---

### 📸 Fixtures Hierarchy

```
SESSION  tests/conftest.py          → clean output/, Allure env.properties, merge logs
  │
FUNCTION tests/ui/conftest.py       → browser launch, video+trace, screenshot on failure
  │
SUITE    tests/ui/pta/conftest.py   → load Excel/YAML testdata for this suite only
```

| Artifact | When kept |
|---|---|
| Screenshot (PNG) | ❌ fail only |
| Video (WebM) | ❌ fail only |
| Trace ZIP | ❌ fail only |
| Allure JSON | ✅ always |
| HTML report | ✅ always |
| Log file | ✅ always |

---

### 📊 Reporting Stack

| Tool | Output | Audience |
|---|---|---|
| **Allure** | `output/allure-results/` → interactive HTML | Stakeholders / PM |
| **pytest-html** | `output/reports/report.html` | Dev / QA team |
| **Rotating log** | `output/logs/test_execution.log` | Debugging |

> Allure `environment.properties` is auto-generated with Browser, OS, Region, Base URL — every report is self-documenting.

---

## 🚀 Running Tests

```powershell
# Set environment (optional — all have defaults)
$env:REGION="QA"; $env:BROWSER="CHROME"; $env:HEADLESS="N"

# UI — PTA suite (parallel)
pytest -vvv -m "pta" -n 4 --reruns 3 --alluredir=output/allure-results tests

# UI — Heroku suite (sequential)
pytest -vvv -m "heroku" --reruns 3 --alluredir=output/allure-results tests

# API — JSONPlaceholder (parallel)
pytest -vvv -m "jsonplaceholder" -n 4 --reruns 3 --alluredir=output/allure-results tests

# One-click executor (run + generate Allure + serve)
cmd /c executor\pta_ui_tests_executor.bat

# Single test
pytest -vvv tests/ui/heroku/test_heroku.py::TestHeroku::test_login
```

---

## 🔁 CI/CD Pipeline (GitHub Actions)

```
Push / PR  →  [lint]  pylint tests + framework  →  must score 10.0/10
                ↓
          [build-and-test]
              pytest -m "pta or heroku" -n 4
                ↓
          Upload allure-report.zip as artifact

Daily schedule: 03:30 UTC
```

---

## 💡 "Why did you choose X?" — Quick Answers

| Decision | One-line Answer |
|---|---|
| **Playwright over Selenium** | Built-in auto-wait, no explicit waits, API testing included, faster |
| **Playwright for API too** | Zero extra dependencies — one tool for UI + API |
| **BasePage pattern** | All Playwright calls in one place — locator strategy changes never touch tests |
| **xdist parallel + shard logs** | 4× faster execution; merged logs = no lost output |
| **REGION env var** | Same binary runs QA → Prod — zero code changes |
| **Locust in same repo** | Reuses config infrastructure — no duplicated URLs or env setup |
| **ADB polling vs sleep** | Reliable emulator startup regardless of machine speed |
| **10.0/10 pylint gate** | Prevents tech debt — CI blocks merges below standard |
| **APKs in repo** | Version-controlled — tests always use the matching app binary |

---

## 🗣️ One-Liner Per Layer

| Layer | One-liner |
|---|---|
| **UI** | Playwright + POM with shared BasePage, parallel execution, Excel data-driven tests |
| **API** | Playwright APIRequestContext wrapped in a thin client for clean CRUD testing |
| **Mobile** | Appium + auto-boot emulator launcher, isolated per-app config, versioned APKs |
| **Performance** | Locust load tests sharing the same config — switch targets with one env var |

---

## 🏁 Adding a New Test Suite (Steps)

```
1. mkdir tests/<type>/<app>/   + __init__.py + conftest.py + test_<app>.py + pages/
2. pytest.ini                  → add new marker
3. config_parser.py            → register new config file paths
4. config/<type>/<app>/        → add YAML / JSON / Excel configs
5. executor/                   → add .bat executor script (optional)
```

---

*Last updated: July 2026 | Framework: Playwright-Python-Automation-Framework*

