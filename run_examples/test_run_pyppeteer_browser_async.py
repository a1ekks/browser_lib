import asyncio

from config import pyppeteer_bin, browser_storage_dir
from browser_lib.pyppeteer_driver.pyppeteer_browser import PyppeteerBrowser
from browser_lib.pyppeteer_driver.pyppeteer_driver import PyppeteerDriver
from utils.custom_logger import CustomLogger


if __name__ == '__main__':

    logger = CustomLogger(
        logger_name='test_pyppeteer_browser_async',
        logger_level=10
    ).logger
    loop = asyncio.get_event_loop()

    _driver = PyppeteerDriver(pyppeteer_bin, is_headless=False)
    pyppeteer_browser = PyppeteerBrowser(
        _driver,
        storage_dir=browser_storage_dir,
        use_auto_screenshot=False,
        logger=logger
    )
    loop.run_until_complete(
        pyppeteer_browser.start_browser()
    )

    # page_content = loop.run_until_complete(
    #     pyppeteer_browser.get_page_content('https://www.lockaway-storage.com/')
    # )
    # print(page_content)

    page_content = loop.run_until_complete(
        pyppeteer_browser.get_page_content_after_click_sequence(
            url='https://www.lockaway-storage.com/',
            waiting_xpath='//div[@class="storage-container"]'
                          '//a[contains(@href, "storage-units")]/@href',
            click_xpath_list=[[
                '//div[contains(@class, "menu-item")]//a[contains(text(), "Storage Locations")]/..',
                '//div[contains(@class, "facilities-container")]'
                '//a[contains(@href, "storage-units")]/@href'
            ]]
        )
    )
    print(page_content)
