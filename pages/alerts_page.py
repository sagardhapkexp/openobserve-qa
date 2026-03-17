import logging
from playwright.sync_api import Page
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class AlertsPage(BasePage):
    """Page object for Alerts, Templates, and Destinations management."""

    # Navigation Locators
    SETTINGS_MENU = "[data-test='menu-link-settings-item']"
    TEMPLATES_TAB = "[data-test='alert-templates-tab']"
    DESTINATIONS_TAB = "[data-test='alert-destinations-tab']"

    # Template Creation Locators
    ADD_TEMPLATE_BTN = "[data-test='template-list-add-btn']"
    TEMPLATE_NAME_LABEL = "Name *"
    HTTP_TAB = "[data-test='tab-http']"
    EDITOR_LINE = ".view-line"
    EDITOR_CONTENT_ROLE = "textbox"
    EDITOR_CONTENT_NAME = "Editor content"
    SUBMIT_TEMPLATE_BTN = "[data-test='add-template-submit-btn']"

    # Destination Creation Locators
    ADD_DESTINATION_BTN = "[data-test='alert-destination-list-add-alert-btn']"
    CUSTOM_DESTINATION_TEXT = "settingsCustom"
    DEST_NAME_INPUT = "[data-test='add-destination-name-input']"
    DEST_TEMPLATE_SELECT = "[data-test='add-destination-template-select']"
    DEST_URL_INPUT = "[data-test='add-destination-url-input']"
    HEADER_KEY_INPUT = "[data-test='add-destination-header--key-input']"
    AUTH_HEADER_VALUE_INPUT = "[data-test='add-destination-header-Authorization-value-input']"
    SUBMIT_DEST_BTN = "[data-test='add-destination-submit-btn']"
    SUCCESS_DEST_MSG = "text=Destination saved successfully"

    # Alert Creation Locators
    NEW_ALERT_BTN_ROLE = "button"
    NEW_ALERT_BTN_NAME = "New alert"
    ALERT_NAME_INPUT = "[data-test='add-alert-name-input']"
    STREAM_TYPE_SELECT = "[data-test='add-alert-stream-type-select-dropdown']"
    STREAM_NAME_SELECT = "[data-test='add-alert-stream-name-select-dropdown']"
    REALTIME_RADIO = "[data-test='add-alert-realtime-alert-radio']"
    CONTINUE_BTN_ROLE = "button"
    CONTINUE_BTN_NAME = "Continue"
    ADD_CONDITION_BTN = "[data-test='alert-conditions-add-condition-btn']"
    COLUMN_INPUT_PLACEHOLDER = "Column"
    VALUE_INPUT_PLACEHOLDER = "Value"
    DEST_SELECT_DROPDOWN = "label:has-text('arrow_drop_down') div:nth-child(4)" # CSS equivalent of original filter logic
    SUBMIT_ALERT_BTN = "[data-test='add-alert-submit-btn']"
    SUCCESS_ALERT_MSG = "text=Alert saved successfully"

    def __init__(self, page: Page) -> None:
        """
        Initialize the AlertsPage.

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

    def create_template(self, template_name: str) -> None:
        """
        Create a new alert template.
        
        Args:
            template_name: Name for the template
        """
        logger.info(f"Creating alert template: {template_name}")
        # Navigate to Settings > Templates
        self.page.locator(self.SETTINGS_MENU).click()
        self.page.wait_for_timeout(500)
        self.page.locator(self.TEMPLATES_TAB).click()
        self.page.wait_for_timeout(500)

        # Click Add Template
        logger.info("Clicking Add Template button")
        self.page.locator(self.ADD_TEMPLATE_BTN).click()
        self.page.wait_for_timeout(500)

        # Fill name
        self.page.get_by_label(self.TEMPLATE_NAME_LABEL).fill(template_name)

        # Click Web Hook tab
        logger.info("Switching to HTTP tab")
        self.page.locator(self.HTTP_TAB).click()
        self.page.wait_for_timeout(500)

        # Fill body in the code editor
        body = '[{"alert_name": "{alert_name}", "stream_name": "{stream_name}", "alert_type": "{alert_type}", "timestamp": "{timestamp}"}]'
        logger.info("Filling template body in editor")
        self.page.locator(self.EDITOR_LINE).click()
        self.page.get_by_role(self.EDITOR_CONTENT_ROLE, name=self.EDITOR_CONTENT_NAME).fill(body)

        # Save
        self.page.wait_for_timeout(2000)
        logger.info("Clicking submit template button")
        self.page.locator(self.SUBMIT_TEMPLATE_BTN).click()
        logger.info("Template save button pressed")

    def create_destination(self, dest_name: str, dest_stream: str, template_name: str) -> None:
        """
        Create a new alert destination.
        
        Args:
            dest_name: Name for the destination
            dest_stream: The stream name to send alerts to
            template_name: The template to use
        """
        logger.info(f"Creating alert destination: {dest_name} (targeting {dest_stream})")
        # Navigate to Settings > Alert Destinations
        self.page.locator(self.SETTINGS_MENU).click()
        self.page.wait_for_timeout(500)
        self.page.locator(self.DESTINATIONS_TAB).click()
        self.page.wait_for_timeout(500)

        # Click Add Destination
        logger.info("Clicking Add Destination button")
        self.page.locator(self.ADD_DESTINATION_BTN).click()
        self.page.wait_for_timeout(500)

        # Select Custom Destination
        logger.info("Selecting Custom Destination type")
        self.page.get_by_text(self.CUSTOM_DESTINATION_TEXT).click()
        self.page.wait_for_timeout(300)

        # Fill Name
        self.page.locator(self.DEST_NAME_INPUT).fill(dest_name)

        # Select Template (type to filter)
        self._select_option(self.page.locator(self.DEST_TEMPLATE_SELECT), template_name)

        # Fill URL
        dest_url = f"http://localhost:5080/api/default/{dest_stream}/_json"
        logger.info(f"Setting destination URL: {dest_url}")
        self.page.locator(self.DEST_URL_INPUT).fill(dest_url)

        # Add Authorization header
        logger.info("Adding Authorization header")
        self.page.locator(self.HEADER_KEY_INPUT).fill("Authorization")
        self.page.locator(self.AUTH_HEADER_VALUE_INPUT).fill(
            "Basic cm9vdEBleGFtcGxlLmNvbTpDb21wbGV4cGFzcyMxMjM="
        )

        # Save
        logger.info("Clicking submit destination button")
        self.page.locator(self.SUBMIT_DEST_BTN).click()

        # Wait for success
        logger.info("Waiting for destination success message")
        self.page.wait_for_selector(self.SUCCESS_DEST_MSG, timeout=5000)

    def create_alert(self, alert_name: str, source_stream: str, dest_name: str) -> None:
        """
        Create a new real-time alert.
        
        Args:
            alert_name: Name for the alert
            source_stream: The stream to monitor
            dest_name: The destination to notify
        """
        logger.info(f"Creating alert: {alert_name} (monitors {source_stream}, notifies {dest_name})")
        # Navigate directly to alerts page
        self.page.goto(f"{self.base_url}/web/alerts")
        self.page.wait_for_timeout(1000)

        # Click New Alert
        logger.info("Clicking New Alert button")
        self.page.get_by_role(self.NEW_ALERT_BTN_ROLE, name=self.NEW_ALERT_BTN_NAME).click()
        self.page.wait_for_timeout(1000)

        # Step 1 — Fill name
        logger.info("Step 1: Filling alert name and selecting stream")
        self.page.locator(self.ALERT_NAME_INPUT).fill(alert_name)

        # Select stream type = logs (type to filter)
        self._select_option(self.page.locator(self.STREAM_TYPE_SELECT), "logs")

        # Select stream name (type to filter)
        self._select_option(self.page.locator(self.STREAM_NAME_SELECT), source_stream)

        # Select Real-time
        self.page.locator(self.REALTIME_RADIO).click()

        # Continue to conditions
        self.page.get_by_role(self.CONTINUE_BTN_ROLE, name=self.CONTINUE_BTN_NAME).click()
        self.page.wait_for_timeout(1000)

        # Step 2 — Add condition: level = error
        logger.info("Step 2: Adding alert conditions")
        self.page.locator(self.ADD_CONDITION_BTN).click()
        self.page.wait_for_timeout(1000)

        self.page.get_by_placeholder(self.COLUMN_INPUT_PLACEHOLDER).click()
        self.page.locator(".q-item__section", has_text="level").first.click()
        self.page.get_by_placeholder(self.VALUE_INPUT_PLACEHOLDER).fill("error")

        # Continue to destination
        self.page.get_by_role(self.CONTINUE_BTN_ROLE, name=self.CONTINUE_BTN_NAME).click()
        self.page.wait_for_timeout(1000)

        # Step 3 — Select destination
        logger.info("Step 3: Selecting alert destination")
        self.page.locator("label").filter(has_text="arrow_drop_down").locator("div").nth(3).click()
        self.page.wait_for_timeout(1000)
        # Type to scroll/find the destination if the list is long
        self.page.keyboard.type(dest_name)
        self.page.wait_for_timeout(500)
        # Select the item
        self.page.locator(".q-menu .q-item").filter(has_text=dest_name).click()

        # Continue to final step
        self.page.get_by_role(self.CONTINUE_BTN_ROLE, name=self.CONTINUE_BTN_NAME).click()
        self.page.wait_for_timeout(1000)

        # Save
        logger.info("Clicking submit alert button")
        self.page.locator(self.SUBMIT_ALERT_BTN).click()
        
        logger.info("Waiting for alert success message")
        self.page.wait_for_selector(self.SUCCESS_ALERT_MSG, timeout=10000)