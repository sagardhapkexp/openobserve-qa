import logging
from playwright.sync_api import Page
import config

logger = logging.getLogger(__name__)

class BasePage:
    """Base class for all page objects, providing shared functionality like login."""

    # Locators as class-level constants
    USERNAME_INPUT = "[data-test='login-user-id']"
    PASSWORD_INPUT = "[data-test='login-password']"
    LOGIN_BUTTON_ROLE = "button"
    LOGIN_BUTTON_NAME = "Login"

    def __init__(self, page: Page) -> None:
        """
        Initialize the BasePage.

        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.base_url = config.BASE_URL

    def login(self) -> None:
        """
        Navigate to the login page and perform authentication using credentials from config.
        """
        logger.info(f"Navigating to login page: {self.base_url}/web/login")
        self.page.goto(f"{self.base_url}/web/login")
        
        username_field = self.page.locator(self.USERNAME_INPUT)
        password_field = self.page.locator(self.PASSWORD_INPUT)
        login_btn = self.page.get_by_role(self.LOGIN_BUTTON_ROLE, name=self.LOGIN_BUTTON_NAME)

        logger.info("Waiting for username input to be visible")
        username_field.wait_for(state="visible")
        
        logger.info(f"Filling credentials for user: {config.EMAIL}")
        username_field.fill(config.EMAIL)
        password_field.fill(config.PASSWORD)
        
        logger.info("Clicking Login button")
        login_btn.click()
        
        logger.info("Waiting for redirect to home page")
        self.page.wait_for_url("**/web/", timeout=10000)
        
        assertion_passed = "web/login" not in self.page.url
        logger.info(f"Login assertion result: {assertion_passed}")
        assert assertion_passed, "Login failed"
