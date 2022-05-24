import time

from config import browser_bin, browser_storage_dir
from browser_lib.browser_enum import BrowserEnum
from browser_lib.browser_factory import BrowserFactory

if __name__ == '__main__':

    pyppeteer_browser_sync = BrowserFactory().create_browser(
        browser_type=BrowserEnum.PYPPETEER_BROWSER,
        bin_path=browser_bin['pyppeteer'],
        storage_dir=browser_storage_dir,
        use_auto_screenshot=True
    )

    selenium_firefox_browser = BrowserFactory().create_browser(
        browser_type=BrowserEnum.SELENIUM_FIREFOX_BROWSER,
        bin_path=browser_bin['firefox'],
        storage_dir=browser_storage_dir,
        use_auto_screenshot=True
    )

    selenium_chrome_browser = BrowserFactory().create_browser(
        browser_type=BrowserEnum.SELENIUM_CHROME_BROWSER,
        bin_path=browser_bin['chrome'],
        storage_dir=browser_storage_dir,
        use_auto_screenshot=True
    )

    browser_list = [
        pyppeteer_browser_sync,
        selenium_chrome_browser,
        selenium_firefox_browser
    ]

    for _browser in browser_list:
        _start_time = time.time()
        _browser.browser_driver.is_headless = True
        _browser.start_browser()
        page_content = _browser.get_page_content(
            'https://www.ipify.org/'
        )
        _browser.stop_browser()
        print(
            f'Browser {_browser.browser_driver.__class__}\n'
            f'Time execute is {time.time() - _start_time}\n'
            f'page content len: {len(page_content)}'
        )

        # print(page_content)


# last results with get content
#
# Browser PyppeteerDriver
# Time execute is 2.2823381423950195
# page content len: 49910
#
# Browser SeleniumChromeDriver
# Time execute is 33.55286240577698
# page content len: 50244
#
# Browser <class SeleniumFirefoxDriver
# Time execute is 41.01983022689819
# page content len: 50369
