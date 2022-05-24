import asyncio
import json
import logging

from browser_lib.interfaces.browser_actions_interface import BrowserActionsInterface
from browser_lib.internal_objects import LoadPageTask
from utils.redis_client import CacheClientAbstract
from utils.rmq_client import QueueClientAbstract


class PageLoaderWorker:

    def __init__(self,
                 cache_client: CacheClientAbstract,
                 queue_client: QueueClientAbstract,
                 logger: logging.Logger,
                 browser: BrowserActionsInterface):

        self.browser = browser
        self.logger = logger
        self.queue_client = queue_client
        self.cache_client = cache_client

    async def load_page(self, task: LoadPageTask):
        method_result = ""

        if not task.method and not hasattr(self.browser, task.method):
            raise ValueError

        current_method = getattr(self.browser, task.method)

        try:
            await self.browser.start_browser()
            self.logger.info('Browser started...')
            method_result = await current_method(**task.dict())

        except Exception as _err:
            self.logger.error(f'Some error: {_err}')

        finally:
            # just screen page for debug if headless True
            await self.browser.get_page_screenshot()
            await self.browser.stop_browser()
            self.logger.info('Browser closed...')

        result_object = {
            'id': task.id,
            'url': task.url,
            'method': task.method,
            'value': json.dumps(method_result)
        }

        return result_object

    async def subscriber_notification(self, loaded_page: dict):
        _id = loaded_page.get('id')
        url = loaded_page.get('url')
        value = loaded_page.get('value')
        method = loaded_page.get('method')

        # FIXME: need one key generation method
        await self.cache_client.set_data(f'{method}_{url}', value)
        await self.cache_client.publish(_id, f'{method}_{url}')

    async def on_new_task(self, queue_message, no_ack=False, task_timeout=30):
        task: dict = json.loads(queue_message.body.decode())
        task: LoadPageTask = LoadPageTask(**task)
        self.logger.info(task)

        try:
            result = await asyncio.wait_for(self.load_page(task), timeout=task_timeout)
        except asyncio.TimeoutError:
            self.logger.error(f'Task {task.id} execution timeout: {task_timeout}')
        except Exception as _err:
            self.logger.error(f'Task {task.id} err {_err}')
        else:
            self.logger.info(f'result task id: {task.id} {result.get("url")}')
            if not no_ack:
                await queue_message.channel.basic_ack(queue_message.delivery.delivery_tag)

            await self.subscriber_notification(result)

    async def run(self):
        self.logger.info('Page loader worker is running...')
        await self.queue_client.get_awaiting_from_queue(no_ack=False, callback_ref=self.on_new_task)
