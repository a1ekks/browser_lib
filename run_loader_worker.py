import asyncio
import uuid

from browser_lib.page_loader_worker import PageLoaderWorker
from browser_lib.pyppeteer_driver.pyppeteer_browser import PyppeteerBrowser
from browser_lib.pyppeteer_driver.pyppeteer_driver import PyppeteerDriver
from config import use_proxy_broker, pyppeteer_bin, is_headless, browser_storage_dir, \
    rabbitmq_config
from utils.custom_logger import configure_worker_logger
from utils.redis_client import redis_cache_client_adapter
from utils.rmq_client import QueueClientAbstract, init_rabbitmq_client_adapter


async def configure_worker(rabbit_config):
    logger = configure_worker_logger('loader_worker', {'worker_id': uuid.uuid4().time})
    rabbitmq_queue_client: QueueClientAbstract = await init_rabbitmq_client_adapter(
        rabbit_config
    )
    redis_cache_client = await redis_cache_client_adapter()

    if use_proxy_broker:
        # TODO: need add proxy broker client
        proxy_object = {}
        _driver = PyppeteerDriver(
            pyppeteer_bin, is_headless=is_headless,
            proxy_item=proxy_object.get('proxy_item'),
            proxy_login=proxy_object.get('proxy_login'),
            proxy_password=proxy_object.get('proxy_password'),
        )
    else:
        _driver = PyppeteerDriver(pyppeteer_bin, is_headless=is_headless)

    pyppeteer_browser = PyppeteerBrowser(
        _driver,
        storage_dir=browser_storage_dir,
        use_auto_screenshot=False,
        logger=logger,
    )

    return PageLoaderWorker(
        queue_client=rabbitmq_queue_client,
        cache_client=redis_cache_client,
        logger=logger,
        browser=pyppeteer_browser
    )

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loader_worker = loop.run_until_complete(configure_worker(rabbitmq_config))
    asyncio.ensure_future(loader_worker.run())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Closing Loop")
        loop.close()
