import asyncio
import json

from browser_lib.internal_objects import LoadPageTask
from config import docker_gateway
from utils.redis_client import CacheClientAbstract
from utils.rmq_client import QueueClientAbstract


class PageLoaderManager:

    def __init__(self,
                 cache_client: CacheClientAbstract,
                 queue_client: QueueClientAbstract,
                 logger):
        self.queue_client = queue_client
        self.cache_client = cache_client
        self.logger = logger

    @classmethod
    async def set_task_url(cls, task_data: LoadPageTask):
        return f'{task_data.method}_{task_data.url}'

    @staticmethod
    async def to_json(parse_task: LoadPageTask) -> str:
        return json.dumps(parse_task.dict())

    @staticmethod
    async def replace_proxy_str(parse_task: LoadPageTask) -> LoadPageTask:
        parse_task.proxy = parse_task.proxy.replace('127.0.0.1', docker_gateway) \
            if parse_task.proxy and '127.0.0.1' in parse_task.proxy else None

        return parse_task

    @classmethod
    async def convert(cls, parse_data: dict) -> LoadPageTask:
        parse_task: LoadPageTask = LoadPageTask(**parse_data)
        parse_task = await cls.replace_proxy_str(parse_task)

        return parse_task

    async def on_page_loaded(self):
        pass

    async def get_page(self, task_data: [dict, LoadPageTask], timeout: int = 60):
        if not isinstance(task_data, LoadPageTask):
            task_data: LoadPageTask = await self.convert(task_data)
        task_url = await self.set_task_url(task_data)
        cache = await self.cache_client.get_data(task_url, to_dict=True)
        if cache:
            return cache

        tasks = [
            asyncio.create_task(self.queue_client.send_to_queue(task_data.dict())),
            asyncio.create_task(self.cache_client.subscribe(task_data.id, timeout=timeout))
        ]

        running_tasks: tuple = await asyncio.gather(*tasks)
        queue_message_id_result, page_load_result = running_tasks

        if page_load_result and page_load_result.get('data'):
            task_page_load_result = await self.cache_client.get_data(
                page_load_result['data'], to_dict=True
            )
            return task_page_load_result

    async def set_task(self, task_data: [dict, LoadPageTask], timeout: int = 60):
        if not isinstance(task_data, LoadPageTask):
            task_data: LoadPageTask = await self.convert(task_data)

        task_url = await self.set_task_url(task_data)
        cache = await self.cache_client.get_data(task_url, to_dict=True)
        if cache:
            return {'url': task_url}

        task_id = await self.queue_client.send_to_queue(task_data.dict())
        if task_id:
            return {'url': task_url}

    async def get_cache(self, url: str):
        return await self.cache_client.get_data(url)
