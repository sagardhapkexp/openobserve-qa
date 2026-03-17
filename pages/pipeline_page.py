import re
import logging
from playwright.sync_api import Page
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

class PipelinePage(BasePage):
    """Page object for Pipelines management."""

    # Locators as class-level constants
    PIPELINE_MENU_LINK      = "[data-test='menu-link-\\/pipeline-item']"
    ADD_PIPELINE_BTN        = "[data-test='pipeline-list-add-pipeline-btn']"
    PIPELINE_NAME_PLACEHOLDER = "Enter Pipeline Name"
    STREAM_TYPE_DROPDOWN    = "div"
    STREAM_NAME_COMBOBOX    = "Stream Name *"
    SAVE_NODE_BTN           = "[data-test='input-node-stream-save-btn']"
    DELETE_NODE_BTN         = "[data-test='input-node-stream-delete-btn']"
    AUTO_OUTPUT_NODE        = "[data-test='pipeline-node-output-stream-node']"
    CONFIRM_BTN             = "[data-test='confirm-button']"
    SOURCE_HANDLE           = "[data-test='pipeline-node-output-input-handle']"
    DEST_HANDLE             = "[data-test='pipeline-node-input-output-handle']"
    SAVE_PIPELINE_BTN       = "[data-test='add-pipeline-save-btn']"

    def __init__(self, page: Page) -> None:
        """
        Initialize the PipelinePage.

        Args:
            page: Playwright Page instance
        """
        super().__init__(page)

    def create_pipeline(self, pipeline_name: str,
                        source_stream: str,
                        dest_stream: str) -> None:
        """
        Create a new pipeline connecting two streams.
        
        Args:
            pipeline_name: Name for the pipeline
            source_stream: Name of the input stream
            dest_stream: Name of the output stream
        """
        logger.info(f"Creating pipeline '{pipeline_name}' connecting '{source_stream}' to '{dest_stream}'")
        # Navigate to Pipelines
        logger.info("Navigating to Pipelines menu")
        self.page.locator(self.PIPELINE_MENU_LINK).click()
        self.page.wait_for_timeout(2000)

        # Click Add Pipeline
        logger.info("Clicking Add Pipeline button")
        self.page.locator(self.ADD_PIPELINE_BTN).click()
        self.page.wait_for_timeout(2000)

        # Fill pipeline name
        logger.info(f"Setting pipeline name: {pipeline_name}")
        name_input = self.page.get_by_placeholder(self.PIPELINE_NAME_PLACEHOLDER)
        name_input.wait_for(state="visible")
        name_input.fill(pipeline_name)
        self.page.wait_for_timeout(500)

        # ─── Source Stream ───
        logger.info("Setting up Source Stream")
        source_btn     = self.page.get_by_role("button", name="Stream").first
        source_btn_box = source_btn.bounding_box()
        src_x          = source_btn_box['x'] + source_btn_box['width'] / 2 # type: ignore
        src_y          = source_btn_box['y'] + source_btn_box['height'] / 2  # type: ignore

        logger.info(f"Dragging source stream node to position (650, 280)")
        self.page.mouse.move(src_x, src_y)
        self.page.mouse.down()
        self.page.wait_for_timeout(500)
        self.page.mouse.move(650, 280, steps=10)
        self.page.mouse.up()
        self.page.wait_for_timeout(1000)

        # Fill source dialog
        logger.info("Filling source stream dialog")
        self.page.wait_for_selector("text=Associate Stream")
        self.page.locator(self.STREAM_TYPE_DROPDOWN).filter(
            has_text=re.compile(r"^logs$")
        ).click()
        self.page.get_by_role("option", name="logs").locator("div").nth(2).click()
        self.page.wait_for_timeout(500)
        
        combobox = self.page.get_by_role("combobox", name=self.STREAM_NAME_COMBOBOX)
        combobox.click()
        self.page.wait_for_timeout(500)
        combobox.fill(source_stream)
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=source_stream).click()
        self.page.wait_for_timeout(500)
        
        logger.info("Saving source node")
        self.page.locator(self.SAVE_NODE_BTN).click()
        self.page.wait_for_timeout(1000)

        # ─── Delete auto output node ───
        logger.info("Deleting auto output node")
        self.page.locator(self.AUTO_OUTPUT_NODE).click()
        self.page.wait_for_timeout(500)
        self.page.locator(self.DELETE_NODE_BTN).click()
        self.page.wait_for_timeout(500)
        self.page.locator(self.CONFIRM_BTN).click()
        self.page.wait_for_timeout(1000)

        # ─── Destination Stream ───
        logger.info("Setting up Destination Stream")
        dest_btn     = self.page.get_by_role("button", name="Stream").nth(1)
        dest_btn_box = dest_btn.bounding_box()
        dst_x        = dest_btn_box['x'] + dest_btn_box['width'] / 2  # type: ignore
        dst_y        = dest_btn_box['y'] + dest_btn_box['height'] / 2  # type: ignore

        logger.info(f"Dragging destination stream node to position (650, 450)")
        self.page.mouse.move(dst_x, dst_y)
        self.page.mouse.down()
        self.page.wait_for_timeout(500)
        self.page.mouse.move(650, 450, steps=10)
        self.page.mouse.up()
        self.page.wait_for_timeout(1000)

        # Fill destination dialog
        logger.info("Filling destination stream dialog")
        self.page.wait_for_selector("text=Associate Stream")
        self.page.locator(self.STREAM_TYPE_DROPDOWN).filter(
            has_text=re.compile(r"^logs$")
        ).click()
        self.page.get_by_role("option", name="logs").locator("div").nth(2).click()
        self.page.wait_for_timeout(500)
        
        dest_combobox = self.page.get_by_role("combobox", name=self.STREAM_NAME_COMBOBOX)
        dest_combobox.click()
        self.page.wait_for_timeout(500)
        dest_combobox.fill(dest_stream)
        self.page.wait_for_timeout(500)
        try:
            self.page.get_by_role("option", name=dest_stream).click(timeout=2000)
        except Exception as e:
            logger.warning(f"Could not click destination stream option: {e}")
            pass
            
        logger.info("Saving destination node")
        self.page.locator(self.SAVE_NODE_BTN).click()
        self.page.wait_for_timeout(1000)

        # ─── Connect nodes ───
        logger.info("Connecting source node handle to destination node handle")
        source_handle = self.page.locator(self.SOURCE_HANDLE)
        dest_handle   = self.page.locator(self.DEST_HANDLE)

        source_box = source_handle.bounding_box()
        dest_box   = dest_handle.bounding_box()

        self.page.mouse.move(
            source_box['x'] + source_box['width'] / 2,  # type: ignore
            source_box['y'] + source_box['height'] / 2   # type: ignore
        )
        self.page.mouse.down()
        self.page.wait_for_timeout(1000)
        self.page.mouse.move( 
            dest_box['x'] + dest_box['width'] / 2,  # type: ignore
            dest_box['y'] + dest_box['height'] / 2,  # type: ignore
            steps=20
        )
        self.page.wait_for_timeout(500)
        self.page.mouse.up()
        self.page.wait_for_timeout(2000)

        # ─── Save pipeline ───
        logger.info("Saving the pipeline")
        self.page.locator(self.SAVE_PIPELINE_BTN).click()
        self.page.wait_for_timeout(1000)
        try:
            self.page.locator(self.CONFIRM_BTN).click(timeout=3000)
        except Exception as e:
            logger.warning(f"Confirm button did not appear: {e}")
            pass
        self.page.wait_for_timeout(2000)