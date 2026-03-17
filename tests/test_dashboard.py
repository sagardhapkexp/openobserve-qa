import time
import pytest
from playwright.sync_api import Page
from pages.dashboard_page import DashboardPage
from helpers.api_helper import ingest_logs


SAMPLE_LOGS = [
    {"level": "info",  "message": "User logged in",      "service": "auth",    "response_time": 120},
    {"level": "error", "message": "DB connection failed", "service": "db",      "response_time": 5000},
    {"level": "info",  "message": "Request completed",    "service": "api",     "response_time": 200},
    {"level": "warn",  "message": "High memory usage",    "service": "api",     "response_time": 800},
    {"level": "error", "message": "Timeout occurred",     "service": "api",     "response_time": 9000},
    {"level": "info",  "message": "Cache hit",            "service": "cache",   "response_time": 10},
    {"level": "debug", "message": "Query executed",       "service": "db",      "response_time": 350},
    {"level": "error", "message": "Auth failed",          "service": "auth",    "response_time": 150},
    {"level": "info",  "message": "File uploaded",        "service": "storage", "response_time": 1200},
    {"level": "warn",  "message": "Rate limit reached",   "service": "api",     "response_time": 450},
]


class TestDashboard:

    def test_dashboard_panel_shows_data(self, logged_in_page, unique_names):
        stream_name    = unique_names["source_stream"]
        dashboard_name = f"qa_dashboard_{int(time.time())}"
        panel_name     = f"qa_panel_{int(time.time())}"

        # Step 1 — Ingest data
        ingest_logs(stream_name, SAMPLE_LOGS)
        time.sleep(3)

        # Step 2 — Create dashboard with panel
        dashboard = DashboardPage(logged_in_page)
        dashboard.create_dashboard_with_panel(
            dashboard_name,
            panel_name,
            stream_name
        )

        # Step 3 — Verify panel has data
        has_data = dashboard.is_panel_showing_data()

        assert has_data, (
            f"Dashboard panel is empty — no data found for stream '{stream_name}'"
        )