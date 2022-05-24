from selenium import webdriver

from browser_lib.interfaces.driver_interface import BrowserDriverInterface


class SeleniumChromeDriver(BrowserDriverInterface):

    def __init__(self,
                 bin_path=None,
                 is_headless=False,
                 proxy_item=None,
                 user_agent=None,
                 browser_args=None):

        self.is_headless = is_headless
        self.proxy_item = proxy_item
        self.user_agent = user_agent
        self.browser_args = browser_args
        self.bin_path = bin_path

        self.driver = None

    def init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-dev-shm-usage")

        options.headless = self.is_headless

        if self.proxy_item:
            _proxy_item = self.set_proxy(self.proxy_item)
            options.add_argument(_proxy_item)

        if self.user_agent:
            _user_agent = self.set_user_agent(self.user_agent)
            options.add_argument(_user_agent)

        _driver = webdriver.Chrome(
            options=options,
            executable_path=self.bin_path
        )

        self.driver = _driver

    def set_proxy(self, proxy_item):
        return f'proxy-server={proxy_item}'

    def set_user_agent(self, user_agent):
        return f'user-agent={user_agent}'

    def driver_stop(self):
        try:
            self.driver.close()
        except Exception:
            pass
