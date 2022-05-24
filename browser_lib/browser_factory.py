from browser_lib.browser_enum import BrowserEnum
from exceptions import NotImplementedBrowserType
from browser_lib.pyppeteer_driver.pyppeteer_browser import PyppeteerBrowserSync
from browser_lib.pyppeteer_driver.pyppeteer_driver import PyppeteerDriver
from browser_lib.selenium_driver.selenium_base_browser import SeleniumBaseBrowser
from browser_lib.selenium_driver.selenium_chrome_driver import SeleniumChromeDriver
from browser_lib.selenium_driver.selenium_firefox_driver import \
    SeleniumFirefoxDriver


class BrowserFactory:

    @staticmethod
    def init_pyppeteer_browser(bin_path, is_headless,
                               proxy_item, user_agent,
                               browser_args, storage_dir,
                               use_auto_screenshot):
        _driver = PyppeteerDriver(bin_path, is_headless, proxy_item,
                                  user_agent, browser_args)

        pyppeteer_browser = PyppeteerBrowserSync(_driver, storage_dir,
                                                 use_auto_screenshot)

        return pyppeteer_browser

    @staticmethod
    def init_selenium_firefox_browser(bin_path, is_headless,
                                      proxy_item, user_agent,
                                      browser_args, storage_dir,
                                      use_auto_screenshot):
        _driver = SeleniumFirefoxDriver(bin_path, is_headless,
                                        proxy_item, user_agent,
                                        browser_args)
        selenium_firefox_browser = SeleniumBaseBrowser(_driver, storage_dir,
                                                       use_auto_screenshot)

        return selenium_firefox_browser

    @staticmethod
    def init_selenium_chrome_browser(bin_path, is_headless,
                                     proxy_item, user_agent,
                                     browser_args, storage_dir,
                                     use_auto_screenshot):

        _driver = SeleniumChromeDriver(bin_path, is_headless,
                                       proxy_item, user_agent,
                                       browser_args)
        selenium_chrome_browser = SeleniumBaseBrowser(_driver, storage_dir,
                                                      use_auto_screenshot)

        return selenium_chrome_browser

    @staticmethod
    def create_browser(browser_type,
                       bin_path=None,
                       is_headless=False,
                       proxy_item=None,
                       user_agent=None,
                       browser_args=None,
                       storage_dir=None,
                       use_auto_screenshot=False):

        if browser_type == BrowserEnum.PYPPETEER_BROWSER:
            return BrowserFactory.init_pyppeteer_browser(
                bin_path, is_headless,
                proxy_item, user_agent,
                browser_args,
                storage_dir,
                use_auto_screenshot
            )

        elif browser_type == BrowserEnum.SELENIUM_CHROME_BROWSER:
            return BrowserFactory.init_selenium_chrome_browser(
                bin_path, is_headless,
                proxy_item, user_agent,
                browser_args,
                storage_dir,
                use_auto_screenshot
            )

        elif browser_type == BrowserEnum.SELENIUM_FIREFOX_BROWSER:
            return BrowserFactory.init_selenium_firefox_browser(
                bin_path, is_headless,
                proxy_item, user_agent,
                browser_args,
                storage_dir,
                use_auto_screenshot
            )

        else:
            raise NotImplementedBrowserType(browser_type)
