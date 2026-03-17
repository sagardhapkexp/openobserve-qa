import pytest
import time
import sys
import os
import logging
import config
from typing import Generator, Dict
from playwright.sync_api import sync_playwright, Page, Browser

# Ensure the project root is in the python path for modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from pages.base_page import BasePage

# Configure logging
def pytest_configure(config):
    """
    Configure logging to write to both console and log file.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("logs/test_run.log", mode="w"),
            logging.StreamHandler(sys.stdout)
        ]
    )

@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """
    Session-scoped fixture to handle browser lifecycle.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        # Teardown: Close the browser after all tests in the session are done
        browser.close()

@pytest.fixture
def logged_in_page(browser: Browser) -> Generator[Page, None, None]:
    """
    Fixture that provides a logged-in Playwright page.
    Automatically logs in using credentials from config.py.
    """
    context = browser.new_context()
    page = context.new_page()
    
    base = BasePage(page)
    base.login()
    
    yield page  # Give the logged-in page to the test
    
    # Teardown: Close the page and context after each test
    page.close()
    context.close()

@pytest.fixture
def unique_stream() -> str:
    """
    Generates a unique stream name for log ingestion tests.
    """
    return f"qa_logs_{int(time.time())}"

@pytest.fixture
def unique_names() -> Dict[str, str]:
    """
    Generates unique names for all alert-related objects.
    All use same timestamp so they're related and easy to find.
    
    Returns:
        Dict containing unique names for template, destination, alert, source_stream, and dest_stream.
    """
    ts = int(time.time())
    return {
        "template":    f"qa_template_{ts}",
        "destination": f"qa_dest_{ts}",
        "alert":       f"qa_alert_{ts}",
        "source_stream": f"qa_source_{ts}",
        "dest_stream":   f"qa_dest_stream_{ts}"
    }

@pytest.fixture(scope="session")
def session_setup() -> None:
    """
    Shared setup for the entire test session.
    """
    logging.info("Starting OpenObserve QA Automation Test Session")
    yield
    logging.info("Completed OpenObserve QA Automation Test Session")
