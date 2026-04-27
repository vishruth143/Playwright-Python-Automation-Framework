# pylint: disable=[missing-function-docstring, missing-module-docstring, redefined-outer-name, unused-argument]
# pylint: disable=[line-too-long, broad-exception-caught, logging-fstring-interpolation,protected-access]

# =============================================================================
# UI CONFTEST – Fixtures & Hooks for All Browser-Based (UI) Tests
# =============================================================================

import os
import logging
import pytest

from framework.utilities.screenshot_utils import get_screenshot_path
from framework.utilities.custom_logger import Logger, set_log_context, clear_log_context

# Lifecycle logger — shared across all test lifecycle hooks in this module.
# file_id "test.lifecycle" mirrors the Selenium framework's log source label.
_lifecycle_log = Logger(file_id="test.lifecycle")

# Stash key used to pass test outcome from the hook → browser_context teardown
_FAILED_KEY = pytest.StashKey[bool]()


# =============================================================================
# FIXTURE: browser_type_launch_args  (overrides pytest-playwright default)
# =============================================================================
# pytest-playwright controls headless mode via this fixture.
# We override it here so our HEADLESS env var (Y/N) is respected instead of
# requiring --headed on the command line.
#
# HEADLESS=Y  → headless  (default – CI / parallel runs)
# HEADLESS=N  → headed    (local debugging)
# =============================================================================
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    headless = os.environ.get("HEADLESS", "Y").upper() != "N"
    return {**browser_type_launch_args, "headless": headless}


# =============================================================================
# FIXTURE: region
# =============================================================================
@pytest.fixture(scope="session")
def region():
    return os.environ.get("REGION", "QA").upper()


# =============================================================================
# FIXTURE: log
# =============================================================================
@pytest.fixture()
def log(request):
    """Return a Logger pre-stamped with worker-id and test-name."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    test_name = request.node.name
    set_log_context(worker_id=worker_id, test_name=test_name)
    logger = Logger(file_id=request.node.module.__name__.rsplit(".", 1)[-1])
    yield logger
    clear_log_context()


# =============================================================================
# FIXTURE: browser_context
# =============================================================================
@pytest.fixture()
def browser_context(browser, request):
    """Create a configured BrowserContext for each test."""
    print('-' * 10 + ' BrowserContext - Setup ' + '-' * 10)

    # Temporary directory for the video – we decide whether to keep or delete
    # it in teardown once we know whether the test passed or failed.
    video_dir = os.path.join(os.getcwd(), "output", "videos")
    os.makedirs(video_dir, exist_ok=True)

    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=video_dir,
        record_video_size={"width": 1920, "height": 1080},
    )

    # Start tracing (screenshots + DOM snapshots)
    context.tracing.start(screenshots=True, snapshots=True)

    # Store context on the node so the hook can reach it
    request.node._browser_context = context

    yield context

    # ------------------------------------------------------------------
    # Teardown – runs AFTER pytest_runtest_makereport has already set
    # the stash key, so we know the true pass/fail outcome here.
    # ------------------------------------------------------------------
    print('-' * 10 + ' BrowserContext - Teardown ' + '-' * 10)

    test_failed = request.node.stash.get(_FAILED_KEY, False)
    safe_name   = request.node.name.replace(" ", "_").replace("[", "_").replace("]", "_")

    # ── Collect the video path BEFORE closing the context ──
    # (after close() the video is written to disk; before close() only the
    #  path is known but the file may still be open / incomplete)
    video_path = None
    try:
        page_obj = request.node.funcargs.get("page")
        if page_obj and page_obj.video:
            video_path = page_obj.video.path()
    except Exception:
        pass

    # ── Stop tracing ──
    try:
        if test_failed:
            trace_dir  = os.path.join(os.getcwd(), "output", "videos")
            trace_path = os.path.join(trace_dir, f"{safe_name}_trace.zip")
            context.tracing.stop(path=trace_path)
        else:
            context.tracing.stop()   # discard – no file written
    except Exception as e:
        logging.warning(f"Could not save/discard trace: {e}")

    # ── Close the context – this finalises + flushes the video file ──
    context.close()

    # ── Delete video for passed tests (file is fully written now) ──
    if not test_failed and video_path:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logging.info(f"Deleted video for passed test: {video_path}")
        except Exception as e:
            logging.warning(f"Could not delete video for passed test: {e}")

    # ── Rename video for failed tests to include the test name ──
    if test_failed and video_path and os.path.exists(video_path):
        try:
            ext         = os.path.splitext(video_path)[1]
            named_path  = os.path.join(os.path.dirname(video_path), f"{safe_name}{ext}")
            os.replace(video_path, named_path)
            logging.info(f"Saved failure video: {named_path}")
        except Exception as e:
            logging.warning(f"Could not rename failure video: {e}")


# =============================================================================
# FIXTURE: page
# =============================================================================
@pytest.fixture()
def page(browser_context, request):
    """Yield a Page from our configured browser context."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    # Strip the parametrise suffix for the test_name context (e.g. "[chromium]")
    raw_name  = request.node.name
    test_name = raw_name.split("[")[0]

    # ── TEST START banner ──
    set_log_context(worker_id=worker_id, test_name=test_name)
    _lifecycle_log.info("-" * 80)
    _lifecycle_log.info(f"TEST START: {test_name}")
    _lifecycle_log.info("-" * 80)

    page = browser_context.new_page()
    request.node._page = page
    yield page
    page.close()

    # ── TEST END banner ──
    set_log_context(worker_id=worker_id, test_name=test_name)
    _lifecycle_log.info("-" * 80)
    _lifecycle_log.info(f"TEST END:   {test_name}")
    _lifecycle_log.info("-" * 80)
    clear_log_context()


# =============================================================================
# HOOK: pytest_runtest_makereport
# =============================================================================
# Captures a screenshot on failure and records the pass/fail outcome in the
# node's stash so browser_context teardown can decide what to do with the video.
# =============================================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On test failure: capture screenshot and mark node as failed."""
    outcome = yield
    rep     = outcome.get_result()

    if rep.when == "call":
        # ── Record outcome in stash (read by browser_context teardown) ──
        if rep.failed:
            item.stash[_FAILED_KEY] = True

        # ── Screenshot on failure ──
        if rep.failed:
            page = getattr(item, "_page", None) or item.funcargs.get("page")
            if page:
                test_name       = item.name
                screenshot_path = get_screenshot_path(test_name)
                try:
                    page.screenshot(path=screenshot_path, full_page=True)
                    logging.info(f"Screenshot captured: {screenshot_path}")
                except Exception as e:
                    logging.error(f"Screenshot capture failed for {test_name}: {e}")
            else:
                logging.warning(f"Test failed but no page fixture found for: {item.name}")
