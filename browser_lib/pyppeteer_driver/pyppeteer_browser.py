import asyncio
import json
import time

from jsonpath import jsonpath

from browser_lib.interfaces.browser_actions_interface import \
    BrowserActionsInterface
from browser_lib.internal_objects import ResponseObject
from utils.helpers import DecoratorHelper, FsHelper

from pyppeteer_stealth import stealth


class PyppeteerBrowser(BrowserActionsInterface):
    """
    Pyppeteer documentation https://miyakogi.github.io/pyppeteer/
    """

    def __init__(self, driver, storage_dir, logger,
                 use_auto_screenshot=False):
        self.logger = logger
        self.browser_driver = driver
        self.storage_dir = storage_dir
        self.use_auto_screenshot = use_auto_screenshot
        self.default_timeout = 85000

    async def start_browser(self):
        await self.browser_driver.init_driver()

    async def get_page_screenshot(self):

        try:
            file_path, file_name = FsHelper.make_fs_file_path(
                self.storage_dir, ext='png'
            )

            current_pages = await self.browser_driver.driver.pages()
            if not len(current_pages):
                return

            current_page = current_pages[-1]

            await current_page.screenshot(
                {'path': file_path}
            )
            self.logger.info(
                f'{current_page.url} has been screened: {file_name}'
            )
        except Exception:
            pass

    async def use_proxy_auth(self, page):
        if all((self.browser_driver.proxy_login, self.browser_driver.proxy_password)):
            await page.authenticate({
                'username': self.browser_driver.proxy_login,
                'password': self.browser_driver.proxy_password
            })

    async def intercept_request(self, req):
        await req.continue_()

    async def intercept_response(self, res):
        if 'ext2020/apub/json/prevent.new' in res.url:
            json_text = await res.text()
            title_li = jsonpath(json.loads(json_text), '$..title')
            for title in title_li:
                print(title)

    async def prevent_default(self, page):

        await page.setJavaScriptEnabled(enabled=True)
        await page.setRequestInterception(True)
        page.on('request', lambda request: asyncio.ensure_future(self.intercept_request(request)))
        page.on(
            'response', lambda response: asyncio.ensure_future(self.intercept_response(response))
        )

        js_text = """() => {
            Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
            window.navigator.chrome = { runtime: {},  };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
        }"""

        await page.evaluateOnNewDocument(js_text)

    async def new_page(self, use_stealth=None, auth_cookies=None):
        page = await self.browser_driver.driver.newPage()

        # get_page_size tkinter doesn't work with graphical interface
        await page.setViewport(viewport={'width': 1280, 'height': 1024})
        await self.prevent_default(page)

        await self.use_proxy_auth(page)

        if use_stealth:
            await stealth(
                page,
            )

        if auth_cookies:
            await page.setCookie(*auth_cookies)

        return page

    async def open_page(self, url, waiting_xpath=None,
                        default_timeout=9000, use_stealth=False,
                        auth_cookies=None) -> ResponseObject:

        response_object = ResponseObject()
        wait_until = {
            'waitUntil': 'domcontentloaded',
            'timeout': default_timeout
        }

        page = await self.new_page(use_stealth=use_stealth, auth_cookies=auth_cookies)
        response = await page.goto(url, wait_until)

        if waiting_xpath:
            try:
                self.logger.debug(
                    f'Waiting xpath: {waiting_xpath}, on page: {url}'
                )
                await page.waitForXPath(waiting_xpath, timeout=default_timeout)
            except Exception as _err:
                self.logger.error(
                    f'XPaths: {waiting_xpath} was not found with time: {default_timeout} '
                    f'Error: {_err}'
                )

        content = await page.content()
        if content:
            self.logger.info(f'The page content completely received, url: {url}')
            response_object.content = content

        response_object.response = response
        response_object.page = page
        response_object.url = url
        response_object.status = response.status

        return response_object

    async def get_page_content(self, url, waiting_xpath=None,
                               default_timeout=9000, use_stealth=False,
                               auth_cookies=None,
                               wait_time=None,
                               *args, **kwargs):

        result: ResponseObject = await self.open_page(
            url=url, waiting_xpath=waiting_xpath,
            default_timeout=default_timeout, use_stealth=use_stealth,
            auth_cookies=auth_cookies
        )

        if wait_time:
            time.sleep(wait_time)

        return {
            'content': result.content,
            'status': result.status
        }

    async def get_page_content_after_click_sequence(self, url,
                                                    click_xpath_list,
                                                    modals_xpath_list=None,
                                                    waiting_xpath=None,
                                                    wait_time=None,
                                                    auth_cookies=None,
                                                    use_stealth=False,
                                                    *args, **kwargs):

        if wait_time is None:
            wait_time = self.default_timeout

        result = await self.open_page(
            url=url,
            waiting_xpath=waiting_xpath,
            default_timeout=wait_time,
            use_stealth=use_stealth,
            auth_cookies=auth_cookies)

        current_page = result.page

        # page = await self.new_page(use_stealth=use_stealth, auth_cookies=auth_cookies)
        #
        # response = await page.goto(url)
        # if waiting_xpath:
        #     await page.waitForXPath(waiting_xpath, timeout=wait_time)
        # pages = await self.browser_driver.driver.pages()
        # current_page = pages[1] if len(pages) > 2 else pages[-1]

        origin_retries = len(click_xpath_list)
        retries = origin_retries

        try:
            while retries:

                for click_xpath_item, waiting_xpath in click_xpath_list:
                    # wait element for clicking element

                    try:
                        await current_page.waitForXPath(click_xpath_item,
                                                        timeout=wait_time)
                    except Exception as _err:
                        self.logger.error(
                            f'Some problem with waiting xpath {click_xpath_item} '
                            f'timeout {wait_time} '
                            f'iteration: {_err} '
                            f'on page: {url} '
                        )
                        continue
                    elements = await current_page.xpath(click_xpath_item)
                    element = elements[0]
                    self.logger.info(
                        f'Try to click with xpath: {click_xpath_item} '
                        f'on element: {element} '
                        f'on page: {url} '
                    )
                    await self.get_page_screenshot()
                    await element.click()
                    self.logger.info(f'Click on element {click_xpath_item}')

                    # waiting content after clicking
                    if waiting_xpath:
                        try:
                            await current_page.waitForXPath(waiting_xpath,
                                                            timeout=wait_time)
                            await self.get_page_screenshot()
                        except Exception as _err:
                            self.logger.error(
                                f'Some problem with waiting xpath: {_err}'
                                f' on page: {url}'
                            )
                        continue

                # check modal and close them FIXME
                if modals_xpath_list:
                    for close_modal_xpath in modals_xpath_list:
                        try:
                            self.logger.info(
                                f'Trying find modals: {close_modal_xpath}'
                            )
                            modal_elements = await current_page.xpath(
                                close_modal_xpath)
                            modal_element = modal_elements[0]
                            await modal_element.click()
                            retries = origin_retries
                        except Exception:
                            pass

                retries -= 1
        except Exception as _err:
            self.logger.error(
                f'Some problems {_err} with click xpaths: {click_xpath_list}'
            )

        return {
            'content': await current_page.content(),
            'status': result.status
        }

    async def get_page_content_after_click_sequence_while_el_exists(
            self, url,
            click_xpath_list,
            default_timeout=85000,
            auth_cookies=None,
            *args,
            **kwargs):
        page = await self.browser_driver.driver.newPage()
        await self.use_proxy_auth(page)

        if auth_cookies:
            await page.setCookie(*auth_cookies)

        await page.goto(url)
        for click_xpath_item, waiting_xpath in click_xpath_list:
            # wait element for clicking element

            while True:
                try:
                    await page.waitForXPath(click_xpath_item,
                                            timeout=default_timeout)

                    elements = await page.xpath(click_xpath_item)
                    element = elements[0]
                    self.logger.info(
                        f'Try to click with xpath: {click_xpath_item}'
                        f' on element: {element}'
                    )
                    await self.get_page_screenshot()
                    await element.click()
                    time.sleep(2)
                except Exception as _err:
                    self.logger.error(
                        f'Some problem with waiting xpath iteration: {_err}')
                    break

            # waiting content after clicking
            if waiting_xpath:
                try:
                    await page.waitForXPath(waiting_xpath,
                                            timeout=default_timeout)
                    await self.get_page_screenshot()
                except Exception as _err:
                    self.logger.error(
                        f'Some problem with waiting xpath: {_err}'
                    )

        content = await page.content()

        return content

    async def check_user_auth(self, xpath):
        pass

    async def auth_logon(self, url, xpath_auth_list):
        timeout_afer_form_step = 0.9
        page = await self.browser_driver.driver.newPage()
        await self.use_proxy_auth(page)
        wait_until = {
            'waitUntil': 'domcontentloaded',
            'timeout': self.default_timeout
        }

        await page.goto(url, wait_until)

        for item_type, item_xpath, item_value in xpath_auth_list:
            if item_type == 'input':
                elements = await page.xpath(item_xpath)
                item_element = elements[0]
                await item_element.type(item_value)
            elif item_type == 'button':
                elements = await page.xpath(item_xpath)
                item_element = elements[0]
                await item_element.click()

            elif item_type == 'waiting_xpath':
                await page.waitForXPath(
                    item_xpath, timeout=self.default_timeout
                )

            time.sleep(timeout_afer_form_step)

        current_cookies = await page.cookies()

        return current_cookies

    async def stop_browser(self):
        await self.browser_driver.driver_stop()
        self.logger.info('Browser closing...')


class PyppeteerBrowserSync(PyppeteerBrowser):

    def __init__(self, driver, storage_dir, auto_screenshot=False):
        super().__init__(driver, storage_dir, auto_screenshot)

    @DecoratorHelper.async_loop
    def start_browser(self):
        return super().start_browser()

    @DecoratorHelper.auto_page_screenshot
    @DecoratorHelper.async_loop
    def get_page_content(self, url, waiting_xpath=None, waiting_load=None,
                         *args, **kwargs):
        return super().get_page_content(
            url, waiting_xpath=None,
            waiting_load=None,
            *args, **kwargs
        )

    @DecoratorHelper.async_loop
    def get_page_content_after_click_sequence(self, url, click_xpath_list,
                                              *args, **kwargs):
        return super().get_page_content_after_click_sequence(
            self, url, click_xpath_list,
            *args, **kwargs
        )

    @DecoratorHelper.async_loop
    def get_page_screenshot(self):
        return super().get_page_screenshot()

    @DecoratorHelper.async_loop
    def stop_browser(self):
        return super().stop_browser()
