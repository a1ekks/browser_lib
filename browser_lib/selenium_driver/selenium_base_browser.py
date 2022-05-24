from browser_lib.interfaces.browser_actions_interface import \
    BrowserActionsInterface
from utils.helpers import DecoratorHelper, FsHelper


class SeleniumBaseBrowser(BrowserActionsInterface):

    def __init__(self, driver, storage_dir, use_auto_screenshot, logger):
        self.logger = logger
        self.use_auto_screenshot = use_auto_screenshot
        self.browser_driver = driver
        self.storage_dir = storage_dir

    def start_browser(self):
        self.browser_driver.init_driver()

    @DecoratorHelper.auto_page_screenshot
    def get_page_content(self, url, waiting_xpath=None, waiting_load=None,
                         *args, **kwargs):
        self.browser_driver.driver.get(url)
        content = self.browser_driver.driver.page_source
        self.logger.debug('Page content completely received')

        return content

    def get_page_content_after_click_sequence(self, url, click_xpath_list,
                                              *args, **kwargs):
        pass

    def get_page_screenshot(self):
        file_path, file_name = FsHelper.make_fs_file_path(
            self.storage_dir, ext='png'
        )
        self.browser_driver.driver.save_screenshot(file_path)

    def stop_browser(self):
        self.browser_driver.driver_stop()
