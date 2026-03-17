import logging
from playwright.sync_api import Page
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class DashboardPage(BasePage):
    """Page object for Dashboards and Panels management."""

    # Menu & Navigation Locators
    DASHBOARDS_MENU = "[data-test='menu-link-/dashboards-item']"
    ADD_DASHBOARD_BTN = "[data-test='dashboard-add']"

    # Add Dashboard Modal Locators
    DASHBOARD_NAME_INPUT = "[data-test='add-dashboard-name']"
    SUBMIT_DASHBOARD_BTN = "[data-test='dashboard-add-submit']"
    SUCCESS_MSG = "text=Dashboard added successfully"

    # Panel Locators
    ADD_PANEL_BTN = "[data-test='dashboard-if-no-panel-add-panel-btn']"
    PANEL_NAME_INPUT = "[data-test='dashboard-panel-name']"
    STREAM_TYPE_DROPDOWN = "[data-test='index-dropdown-stream_type']"
    STREAM_DROPDOWN = "[data-test='index-dropdown-stream']"
    CUSTOM_QUERY_TYPE_BTN = "[data-test='dashboard-custom-query-type']"
    EDITOR_CONTENT_ROLE = "textbox"
    EDITOR_CONTENT_NAME = "Editor content"
    APPLY_BTN = "[data-test='apply-button']" # Assuming the user meant this based on context, but let's stick to their selector if possible. Wait, original was "[data-test='dashboard-apply']"
    APPLY_BTN_SELECTOR = "[data-test='dashboard-apply']"
    SAVE_PANEL_BTN = "[data-test='dashboard-panel-save']"
    
    # Checks Locators
    NO_DATA_TEXT = "text=No Data"

    def __init__(self, page: Page) -> None:
        """
        Initialize the DashboardPage.

        Args:
            page: Playwright Page instance
        """
        super().__init__(page)

    def _select_option(self, dropdown_locator, option_text: str) -> None:
        """
        Open a Quasar QSelect dropdown, type to filter the options,
        then click the matching option.
        
        Args:
            dropdown_locator: The locator for the dropdown element
            option_text: The text of the option to select
        """
        logger.info(f"Selecting option '{option_text}' from dropdown")
        dropdown_locator.click()
        self.page.wait_for_timeout(500)

        # Type into the active input to filter the option list
        self.page.keyboard.type(option_text)
        self.page.wait_for_timeout(500)

        # Wait for the filtered option and click it
        option = self.page.get_by_role("option", name=option_text, exact=True).first
        option.wait_for(state="visible", timeout=5000)
        option.click()
        self.page.wait_for_timeout(300)

    def create_dashboard_with_panel(self, dashboard_name: str,
                                     panel_name: str,
                                     stream_name: str) -> None:
        """
        Create a new dashboard and add a panel with a custom SQL query.
        
        Args:
            dashboard_name: Name for the dashboard
            panel_name: Name for the panel
            stream_name: Name of the stream to query
        """
        logger.info(f"Creating dashboard '{dashboard_name}' with panel '{panel_name}' for stream '{stream_name}'")
        # Navigate to Dashboards
        self.page.locator(self.DASHBOARDS_MENU).click()
        self.page.wait_for_timeout(1000)

        # Click New Dashboard
        logger.info("Clicking Add Dashboard button")
        self.page.locator(self.ADD_DASHBOARD_BTN).click()
        self.page.wait_for_timeout(1000)

        # Fill name
        self.page.locator(self.DASHBOARD_NAME_INPUT).fill(dashboard_name)
        self.page.wait_for_timeout(500)

        # Click Save
        logger.info("Submitting dashboard creation")
        submit_btn = self.page.locator(self.SUBMIT_DASHBOARD_BTN)
        submit_btn.wait_for(state="visible")
        submit_btn.click()
        self.page.locator(self.SUCCESS_MSG).wait_for(state="visible")
        self.page.wait_for_timeout(1000)

        # Add panel
        logger.info("Clicking Add Panel button")
        add_panel = self.page.locator(self.ADD_PANEL_BTN)
        add_panel.wait_for(state="visible")
        add_panel.click()
        self.page.wait_for_timeout(1000)

        # Fill panel name
        self.page.locator(self.PANEL_NAME_INPUT).fill(panel_name)
        self.page.wait_for_timeout(500)

        # Select stream type = logs
        self._select_option(self.page.locator(self.STREAM_TYPE_DROPDOWN), "logs")

        # Select stream name
        self._select_option(self.page.locator(self.STREAM_DROPDOWN), stream_name)

        # Click Custom query mode
        logger.info("Switching to Custom Query mode")
        self.page.locator(self.CUSTOM_QUERY_TYPE_BTN).click()
        self.page.wait_for_timeout(500)

        # Fill SQL query
        sql = (
            f"SELECT histogram(_timestamp) AS x_axis_1, "
            f"avg(response_time) AS y_axis_1 "
            f"FROM \"{stream_name}\" "
            f"GROUP BY x_axis_1 "
            f"ORDER BY x_axis_1 ASC"
        )
        logger.info(f"Filling SQL query: {sql}")
        editor = self.page.get_by_role(self.EDITOR_CONTENT_ROLE, name=self.EDITOR_CONTENT_NAME)
        editor.press("Control+a")
        editor.fill(sql)
        self.page.wait_for_timeout(500)

        # Apply first to generate fields
        logger.info("Applying query to generate fields")
        self.page.locator(self.APPLY_BTN_SELECTOR).click()
        self.page.wait_for_timeout(2000)

        # Add y_axis_1 to Y-axis
        logger.info("Adding y_axis_1 to Y-axis")
        self.page.locator(
            f"[data-test='field-list-item-logs-{stream_name}-y_axis_1'] "
            f"[data-test='dashboard-add-y-data']"
        ).click()
        self.page.wait_for_timeout(500)

        # Apply again with Y-axis selected
        logger.info("Applying query again with Y-axis selected")
        self.page.locator(self.APPLY_BTN_SELECTOR).click()
        self.page.wait_for_timeout(3000)

        # Save panel
        logger.info("Saving panel")
        save_btn = self.page.locator(self.SAVE_PANEL_BTN)
        save_btn.wait_for(state="visible")
        save_btn.click()
        self.page.wait_for_timeout(2000)

    def is_panel_showing_data(self) -> bool:
        """
        Check if the panel is showing data or 'No Data'.
        
        Returns:
            True if panel has data, False if No Data message is present.
        """
        count = self.page.locator(self.NO_DATA_TEXT).count()
        has_data = count == 0
        logger.info(f"Checking if panel shows data: {has_data}")
        return has_data
