
class BaseExeption(Exception):
    pass


class NotImplementedBrowserType(BaseExeption):
    def __init__(self, browser_type):
        self.browser_type = browser_type

    def __str__(self):
        return f'This type of browser {self.browser_type} not implemented'


class MethodIsNotImplemented(BaseExeption):
    def __init__(self, method_str):
        self.method_str = method_str

    def __str__(self):
        return f'Method: {self.method_str} must be implemented'
