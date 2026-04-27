# pylint: disable=[unused-argument, missing-module-docstring, unspecified-encoding]
# pylint: disable=[missing-function-docstring, line-too-long, broad-exception-caught]

import os
import shutil
import stat
import logging
import json
import platform

from framework.utilities.custom_logger import merge_worker_logs, Logger, set_log_context, clear_log_context


def _on_rm_error(func, path, exc_info):
    """Handle read-only / locked files during shutil.rmtree."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        print(f"Could not delete locked file: {path}")


def _release_log_handlers():
    """
    Close every file handler on every active logger so that Windows releases
    the OS-level lock on test_execution.log before shutil.rmtree runs.
    """
    for name, logger in list(logging.Logger.manager.loggerDict.items()):
        if isinstance(logger, logging.Logger):
            for handler in list(logger.handlers):
                try:
                    handler.flush()
                    handler.close()
                except Exception:
                    pass
                logger.removeHandler(handler)


def pytest_sessionstart(session):
    """Clean up and re-create the output directory at the start of every test run."""

    # xdist worker processes also fire pytest_sessionstart, but all cleanup,
    # allure setup, and log-header writing must only happen ONCE on the
    # controller process.  Workers skip everything here.
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return

    _release_log_handlers()

    output_dir = os.path.join(os.getcwd(), 'output')
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir, onerror=_on_rm_error)
            print(f"Cleaned up output directory: {output_dir}")
        except Exception as e:
            print(f"Failed to clean output directory {output_dir}: {e}")
    else:
        print(f"Output directory does not exist, no cleanup needed: {output_dir}")

    # Re-create all required output subdirectories
    for subdir in ('allure-results', 'logs', 'reports', 'screenshots', 'videos'):
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)

    # Write environment.properties for the Allure "Environment" widget
    env_file_path = os.path.join(output_dir, 'allure-results', 'environment.properties')
    with open(env_file_path, 'w') as f:
        f.write(f"REGION={os.getenv('REGION', 'QA')}")
        f.write(f"\nBROWSER={os.getenv('BROWSER', 'CHROMIUM')}")
        f.write(f"\nHEADLESS={os.getenv('HEADLESS', 'N')}")

    # Copy categories.json into allure-results so the Allure "Categories" tab
    # groups failures into meaningful buckets (Product Defects, Test Defects, etc.)
    categories_src = os.path.join(os.getcwd(), 'config', 'categories.json')
    categories_dst = os.path.join(output_dir, 'allure-results', 'categories.json')
    if os.path.exists(categories_src):
        shutil.copy2(categories_src, categories_dst)
        print(f"Copied categories.json to: {categories_dst}")

    # Generate executor.json for the Allure "Executors" widget
    executor_data = _build_executor_info()
    executor_path = os.path.join(output_dir, 'allure-results', 'executor.json')
    with open(executor_path, 'w') as f:
        json.dump(executor_data, f, indent=2)
    print(f"Generated executor.json: {executor_data.get('name')}")

    # Write the session header banner to test_execution.log (controller only)
    _log_session_header(executor_data)


def _log_session_header(executor_data: dict) -> None:
    """
    Write a prominent session-start banner to test_execution.log.

    Format written to the file:

        ================================================================================
          Worker: main
        ================================================================================
        <timestamp>  [main  ]  [session]  INFO  session:...:  ================...
        <timestamp>  [main  ]  [session]  INFO  session:...:  Pytest session started ...
        <timestamp>  [main  ]  [session]  INFO  session:...:  ================...
    """
    set_log_context(worker_id="main", test_name="session")
    try:
        # Write the worker separator block directly to the file BEFORE the Logger
        # opens it, so it appears at the very top (matches the xdist worker format).
        log_file = os.path.join(os.getcwd(), "output", "logs", "test_execution.log")
        with open(log_file, "a", encoding="utf-8") as fh:
            fh.write(f"\n{'=' * 80}\n  Worker: main\n{'=' * 80}\n")

        session_log = Logger(file_id="session")
        executor_name = executor_data.get("name", "Unknown")
        region        = os.getenv("REGION", "QA").upper()
        browser       = os.getenv("BROWSER", "CHROMIUM").upper()
        headless      = os.getenv("HEADLESS", "N").upper()
        session_log.info("=" * 80)
        session_log.info(
            f"Pytest session started - executor={executor_name}, "
            f"region={region}, browser={browser}, headless={headless}"
        )
        session_log.info("=" * 80)
    finally:
        clear_log_context()


def pytest_sessionfinish(session, exitstatus):
    """
    Merge per-worker log shards into a single test_execution.log.

    pytest-xdist workers each write to their own shard file
    (test_execution_gw0.log, test_execution_gw1.log, …) to avoid cross-
    process write contention.  This hook runs on the *controller* process
    after all workers have finished, so all shards are fully flushed and
    safe to read and merge.
    """
    # Only the controller process (no PYTEST_XDIST_WORKER env var) should merge.
    if not os.environ.get("PYTEST_XDIST_WORKER"):
        try:
            merge_worker_logs()
            print("Merged worker log shards into test_execution.log")
        except Exception as e:
            print(f"Warning: could not merge worker logs: {e}")


def _build_executor_info() -> dict:
    """Return executor metadata for Allure (GitHub Actions / Jenkins / local)."""
    # --- GitHub Actions ---
    if os.getenv('GITHUB_ACTIONS') == 'true':
        server_url = os.getenv('GITHUB_SERVER_URL', 'https://github.com')
        repo = os.getenv('GITHUB_REPOSITORY', '')
        run_id = os.getenv('GITHUB_RUN_ID', '')
        run_number = os.getenv('GITHUB_RUN_NUMBER', '0')
        build_url = f"{server_url}/{repo}/actions/runs/{run_id}"
        return {
            "name": "GitHub Actions",
            "type": "github",
            "buildName": f"Run #{run_number}",
            "buildUrl": build_url,
            "buildOrder": int(run_number),
            "reportUrl": build_url,
        }

    # --- Jenkins ---
    if os.getenv('JENKINS_URL'):
        return {
            "name": "Jenkins",
            "type": "jenkins",
            "buildName": os.getenv('BUILD_DISPLAY_NAME', os.getenv('BUILD_NUMBER', 'N/A')),
            "buildUrl": os.getenv('BUILD_URL', ''),
            "buildOrder": int(os.getenv('BUILD_NUMBER', '0')),
            "reportUrl": os.getenv('BUILD_URL', ''),
        }

    # --- Local machine ---
    return {
        "name": f"Local ({platform.node()})",
        "type": "local",
        "buildName": f"{platform.system()} {platform.release()}",
    }
