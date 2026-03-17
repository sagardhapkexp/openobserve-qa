import time
from pages.alerts_page import AlertsPage
from helpers.api_helper import ingest_logs, search_logs


class TestAlertsRealTime:

    def test_real_time_alert_triggers(self, logged_in_page, unique_names):
        # SETUP — create source stream via API
        source_stream = unique_names["source_stream"]
        dest_stream   = unique_names["dest_stream"]
        template_name = unique_names["template"]
        dest_name     = unique_names["destination"]
        alert_name    = unique_names["alert"]

        # Step 1 — Ingest initial log to create source stream
        ingest_logs(source_stream, [{"level": "info", "message": "setup"}])
        time.sleep(2)

        # Step 2 — Create Template, Destination, Alert via UI
        alerts = AlertsPage(logged_in_page)
        alerts.create_template(template_name)
        alerts.create_destination(dest_name, dest_stream, template_name)
        alerts.create_alert(alert_name, source_stream, dest_name)

        # Step 3 — Ingest triggering log (level=error fires the alert)
        ingest_logs(source_stream, [{"level": "error", "message": "DB failed"}])

        # Step 4 — Wait for alert pipeline to process
        print("Waiting for alert pipeline...")
        time.sleep(15)

        # Step 5 — Verify destination stream received alert data
        hits = search_logs(dest_stream)

        assert len(hits) > 0, (
            f"Alert did not fire — destination stream '{dest_stream}' is empty. "
            f"Check if alert '{alert_name}' is active."
        )

        # Step 6 — Verify alert fields exist
        first_hit = hits[0]
        assert "alert_name" in first_hit, (
            f"Expected 'alert_name' field in alert data but got: {first_hit}"
        )