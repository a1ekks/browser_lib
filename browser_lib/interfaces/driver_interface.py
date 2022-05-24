from abc import ABC, abstractmethod


class BrowserDriverInterface(ABC):

    @abstractmethod
    def init_driver(self):
        pass

    @abstractmethod
    def set_proxy(self, proxy_item):
        pass

    @abstractmethod
    def set_user_agent(self, user_agent):
        pass

    @abstractmethod
    def driver_stop(self):
        pass
