import time
from helpers.api_helper import ingest_logs, search_logs

SAMPLE_LOGS = [
    {"level": "info",  "message": "User logged in",             "user_id": "u001"},
    {"level": "error", "message": "Database connection failed", "code": 500},
    {"level": "info",  "message": "Request completed",          "took_ms": 142},
    {"level": "warn",  "message": "High memory usage",          "threshold": 90},
    {"level": "debug", "message": "Cache miss",                 "key": "session_42"}
]


class TestLogsIngestions:

    def test_ingestion_returns_200(self, unique_stream):
        response = ingest_logs(unique_stream, SAMPLE_LOGS)
        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}. "
            f"Response: {response.text}"
        )

    def test_ingested_count_matches(self, unique_stream):
        ingest_logs(unique_stream, SAMPLE_LOGS)
        time.sleep(2)

        hits = search_logs(unique_stream)
        assert len(hits) == len(SAMPLE_LOGS)

    def test_fields_values_are_correct(self, unique_stream):
        ingest_logs(unique_stream, SAMPLE_LOGS)
        time.sleep(2)

        hits = search_logs(unique_stream)

        returned_messages = {hit["message"] for hit in hits}
        expected_messages = {log["message"] for log in SAMPLE_LOGS}

        missing = expected_messages - returned_messages

        assert not missing, (
            f"These messages were not found in results: {missing}"
        )

    def test_sql_filter_returns_only_errors(self, unique_stream):
        ingest_logs(unique_stream, SAMPLE_LOGS)
        time.sleep(3)

        sql = f"SELECT * FROM \"{unique_stream}\" WHERE level = 'error'"
        hits = search_logs(unique_stream, sql=sql)

        assert len(hits) == 1, (
            f"Expected 1 error record but got {len(hits)}."
        )
        assert hits[0]["message"] == "Database connection failed", (
            f"Wrong record returned: {hits[0]}"
        )
