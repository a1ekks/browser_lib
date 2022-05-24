import uuid

from pyppeteer.network_manager import Response
from pyppeteer.page import Page
from typing import List, Optional
from pydantic import BaseModel


class ResponseObject:

    url: str = None
    content: str = None
    response: Response = None
    page: Page = None
    status: int = None


class LoadPageTask(BaseModel):

    id: str = str(uuid.uuid4())
    method: str
    url: str
    waiting_xpath: Optional[str] = None
    click_xpath_list: Optional[List[List[str]]] = None
    modals_xpath_list: Optional[List[List[str]]] = None
    wait_time: Optional[int] = None
    use_cache: Optional[bool] = False
    save_cache: Optional[bool] = False
    proxy: Optional[str] = None
    use_stealth: Optional[bool] = False
    is_headless: Optional[bool] = True
    clean: Optional[bool] = True
    to_json: Optional[bool] = True


class PageContent(BaseModel):
    url: str
    clean: Optional[bool] = True
    to_json: Optional[bool] = True


class CacheObject(BaseModel):
    content: str
    status: int


if __name__ == '__main__':
    external_data = {
        'id': 'f2d96a6c-f5fd-4bdf-85ff-32fc60224c37',
        'method': 'get_page_content_after_click_sequence',
        'url': 'https://www.lockaway-storage.com', 'click_xpath_list': [[
            '//div[contains(@class, "menu-item")]//a[contains(text(), "Storage Locations")]/..',
            '//div[contains(@class, "facilities-container")]'
            '//a[contains(@href, "storage-units")]/@href'
        ]],
        'modals_xpath_list': None}
    tt = LoadPageTask(**external_data)

    print(tt)
