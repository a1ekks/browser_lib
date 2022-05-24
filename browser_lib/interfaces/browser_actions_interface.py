from abc import ABC, abstractmethod


class BrowserActionsInterface(ABC):

    @abstractmethod
    def start_browser(self):
        pass

    @abstractmethod
    def get_page_content(self,
                         url,
                         waiting_xpath=None,
                         waiting_load=None,
                         *args, **kwargs):
        pass

    @abstractmethod
    def get_page_content_after_click_sequence(self,
                                              url,
                                              click_xpath_list,
                                              *args, **kwargs):
        pass

    @abstractmethod
    def get_page_screenshot(self):
        pass

    @abstractmethod
    def stop_browser(self):
        pass
