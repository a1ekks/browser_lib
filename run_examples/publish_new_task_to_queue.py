import asyncio
import logging

from browser_lib.page_loader_manager import PageLoaderManager
from utils.redis_client import redis_cache_client_adapter
from utils.rmq_client import QueueClientAbstract, init_rabbitmq_client_adapter

if __name__ == "__main__":
    rabbitmq_config = {
        'host': '127.0.0.1',
        'port': 5672,
        'login': 'browserlib',
        'password': 'browserlib123',
        'virtualhost': 'browser_parsing'
    }

    event_loop = asyncio.get_event_loop()
    rabbitmq_queue_client: QueueClientAbstract = event_loop.run_until_complete(
        init_rabbitmq_client_adapter(rabbitmq_config, event_loop)
    )

    redis_cache_client = event_loop.run_until_complete(redis_cache_client_adapter())
    logger = logging.getLogger('test_worker')

    page_loader = PageLoaderManager(
        queue_client=rabbitmq_queue_client,
        cache_client=redis_cache_client,
        logger=logger
    )

    data = dict(
        method='get_page_content_after_click_sequence',
        url='https://www.lockaway-storage.com/',
        waiting_xpath='//div[@class="storage-container"]'
                      '//a[contains(@href, "storage-units")]/@href',
        click_xpath_list=[[
            '//div[contains(@class, "menu-item")]//a[contains(text(), "Storage Locations")]/..',
            '//div[contains(@class, "facilities-container")]'
            '//a[contains(@href, "storage-units")]/@href'
        ]]
    )

    event_loop.run_until_complete(page_loader.get_page(data))
