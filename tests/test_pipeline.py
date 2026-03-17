import re
import time
import pytest
from playwright.sync_api import Page
from pages.pipeline_page import PipelinePage
from helpers.api_helper import ingest_logs, search_logs


class TestPipeline:

    def test_pipeline_routes_data(self, logged_in_page, unique_names):
        source_stream = unique_names["source_stream"]
        dest_stream   = unique_names["dest_stream"]
        pipeline_name = f"qa_pipeline_{int(time.time())}"

        # Step 1 — Create source stream
        ingest_logs(source_stream, [
            {"level": "info",  "message": "User logged in",  "service": "auth"},
            {"level": "error", "message": "DB failed",       "service": "db"},
            {"level": "warn",  "message": "High memory",     "service": "api"},
        ])
        time.sleep(2)

        # Step 2 — Create pipeline via UI
        pipeline = PipelinePage(logged_in_page)
        pipeline.create_pipeline(pipeline_name, source_stream, dest_stream)

        # Step 3 — Ingest triggering data
        ingest_logs(source_stream, [
            {"level": "error", "message": "Pipeline test log 1"},
            {"level": "info",  "message": "Pipeline test log 2"},
            {"level": "warn",  "message": "Pipeline test log 3"},
        ])

        # Step 4 — Wait for pipeline to process
        print("Waiting for pipeline...")
        time.sleep(5)

        # Step 5 — Verify data in destination stream
        hits = search_logs(dest_stream)

        assert len(hits) > 0, (
            f"Pipeline did not route data — "
            f"destination stream '{dest_stream}' is empty"
        )

        # Step 6 — Verify field values
        messages = {hit["message"] for hit in hits}
        assert "Pipeline test log 1" in messages, (
            f"Expected log not found in destination stream. Got: {messages}"
        )