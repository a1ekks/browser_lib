
from pyppeteer import launch, launcher

from browser_lib.interfaces.driver_interface import BrowserDriverInterface


class PyppeteerDriver(BrowserDriverInterface):

    def __init__(self,
                 bin_path=None,
                 is_headless=False,
                 proxy_item=None,
                 user_agent=None,
                 browser_args=None,
                 proxy_login=None,
                 proxy_password=None,
                 ignore_http_errors=True,
                 not_use_stdout=True):

        self.not_use_stdout = not_use_stdout
        self.ignore_http_errors = ignore_http_errors
        self.bin_path = bin_path
        self.is_headless = is_headless
        self.proxy_item = proxy_item
        self.user_agent = user_agent
        self.browser_args = browser_args
        self.proxy_login = proxy_login
        self.proxy_password = proxy_password

        self.driver = None

    async def set_user_agent(self, user_agent):
        user_agent_str = '--user-agent={}'.format(user_agent)

        return user_agent_str

    async def set_proxy(self, proxy_item):
        proxy_item_str = '--proxy-server={}'.format(proxy_item)

        return proxy_item_str

    async def init_driver(self):
        remove_from_default = ("--enable-automation",)
        for del_item in remove_from_default:
            if del_item not in launcher.DEFAULT_ARGS:
                continue
            launcher.DEFAULT_ARGS.remove(del_item)
        default_args = [
            '--no-first-run',
            '--no-default-browser-check',
            '--no-sandbox',
            '--disable-notifications',
            '--disable-infobars',
            '--start-maximized',
            '--window-size=1920,1080'
        ]
        browser_args = []
        browser_args.extend(default_args)

        if self.browser_args:
            browser_args.extend(self.browser_args)

        if self.proxy_item:
            browser_args.append(await self.set_proxy(self.proxy_item))

        if self.user_agent:
            browser_args.append(await self.set_user_agent(self.user_agent))

        _browser_args = list(set(browser_args))

        if self.bin_path:
            pyppeteer_driver = await launch({
                'headless': self.is_headless,
                'dumpio': self.not_use_stdout,
                'ignorehttpserrrors': self.ignore_http_errors,
                'args': _browser_args,
                'executablePath': self.bin_path
            })
        else:
            pyppeteer_driver = await launch({
                'headless': self.is_headless,
                'args': _browser_args
            })

        self.driver = pyppeteer_driver

    async def driver_stop(self):
        try:
            await self.driver.close()
        except Exception:
            pass
