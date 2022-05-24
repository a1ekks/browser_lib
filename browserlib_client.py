import json


class BrowserLibClientBase:
    def __init__(self):
        # basic client params
        self.browserlib_api_url = None
        # api methods
        self.method = None
        self.waiting_xpath = None
        self.method_xpath_sequence = None
        self.url = None
        # cache
        self.use_cache = None
        self.save_cache = None

    @staticmethod
    def convert_to_url_params(data_dict):
        api_url = data_dict.pop('browserlib_api_url')
        api_method = data_dict.pop('method')

        params_str = '&'.join(
            '{}={}'.format(
                param_name,
                json.dumps(param_value) if isinstance(param_value, list)
                else param_value
            ) for param_name, param_value in data_dict.items()
            if param_value
        )

        url_with_params = f'{api_url}/{api_method}?{params_str}'

        return url_with_params


class BrowserLibClient:
    def __init__(self, client=BrowserLibClientBase()):
        self.client = client

    @property
    def api_settings(self):
        return BrowserLibApiSettings(self.client)

    @property
    def method(self):
        return BrowserLibClientMethod(self.client)

    @property
    def cache(self):
        return BrowserLibClientUsingCache(self.client)

    def set_client(self):
        return self.client.convert_to_url_params(self.client.__dict__)


class BrowserLibApiSettings(BrowserLibClient):

    def __init__(self, client):
        super().__init__(client)

    def set_api_url(self, api_url):
        self.client.browserlib_api_url = api_url

        return self


class BrowserLibClientMethod(BrowserLibClient):

    def __init__(self, client):
        super().__init__(client)

    def set_method(self, client_method):
        self.client.method = client_method

        return self

    def waiting_xpath(self, xpath):
        self.client.waiting_xpath = xpath

        return self

    def method_xpath_sequence(self, xpath_list):
        self.client.method_xpath_sequence = xpath_list

        return self

    def page_url(self, url):
        self.client.url = url

        return self


class BrowserLibClientUsingCache(BrowserLibClient):

    def __init__(self, client):
        super().__init__(client)

    def use_cache(self, use_cache=False):
        self.client.use_cache = use_cache

        return self

    def save_cache(self, save_cache=False):
        self.client.save = save_cache

        return self


if __name__ == '__main__':
    """
    http://127.0.0.1:8080/get_page_content
    ?waiting_xpath=//span[contains(@class, "sss-location")]/a/@href
    &url=https://www.devonselfstorage.com/locations
    &use_cache=True
    &save=True
    """

    api_url = 'http://127.0.0.1:8080'
    browser_lib_client = BrowserLibClient(). \
        api_settings.set_api_url(api_url). \
        method. \
        set_method('get_page_content'). \
        waiting_xpath('//span[contains(@class, "sss-location")]/a/@href').\
        page_url('https://www.devonselfstorage.com/locations'). \
        cache.use_cache(True). \
        save_cache(True). \
        set_client()
