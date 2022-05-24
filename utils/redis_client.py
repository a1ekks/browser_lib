import json
import logging
from abc import ABC, abstractmethod

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


class CacheClientAbstract(ABC):

    @abstractmethod
    async def init_connection(self):
        pass

    @abstractmethod
    async def get_data(self, key: str, to_dict: bool = False):
        pass

    @abstractmethod
    async def get_channels(self):
        pass

    @abstractmethod
    async def get_keys_by_template(self, template="*"):
        pass

    @abstractmethod
    async def set_data(self, key: str, value: str):
        pass

    @abstractmethod
    async def delete_data(self, key):
        pass

    @abstractmethod
    async def delete_all_data(self):
        pass

    @abstractmethod
    async def publish(self, channel: str, msg: str):
        pass

    @abstractmethod
    async def subscribe(self, channel: str, timeout: int = 60):
        pass

    @abstractmethod
    async def close_connection(self):
        pass


async def redis_cache_client_adapter(**kwargs) -> CacheClientAbstract:
    redis_cache_client = RedisCacheClientAsync(**kwargs)
    await redis_cache_client.init_connection()

    return redis_cache_client


class RedisCacheClientAsync(CacheClientAbstract):

    def __init__(
            self,
            host: str = '127.0.0.1',
            port: int = 6379,
            db_name: str = None,
            db_names: tuple = ('',),
            user: str = None,
            password: str = None,
            cache_ttl_seconds: int = 3600):

        self.cache_ttl_seconds = cache_ttl_seconds
        self.password = password
        self.user = user
        self.port = port
        self.host = host
        self.redis_db = db_names.index(db_name) if db_name and db_name in db_names else None

        self.connection = None

    async def __aenter__(self):
        if not self.connection:
            await self.init_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()

    async def init_connection(self):
        self.connection = await aioredis.from_url(
            'redis://', port=self.port,
            host=self.host,
            username=self.user,
            password=self.password,
            db=self.redis_db
        )

    async def get_data(self, key: str, to_dict=False):
        result: bytes = await self.connection.get(name=key)
        if not result:
            return
        result: str = result.decode()
        if to_dict:
            result: dict = json.loads(result)

        return result

    async def get_channels(self):
        return await self.connection.pubsub_channels()

    async def get_keys_by_template(self, template="*"):
        async for row in self.connection.scan_iter(match="*" + template + "*"):
            yield row.decode()

    async def get_all_records_by_key(self, key: str):
        try:
            msgs_results = await self.connection.hgetall(key)
        except Exception as _err:
            logger.error(f'Error with getting msgs by key {_err}')
        else:
            # TODO: need to optimize
            return [
                msgs_results.get(i).decode()
                for i in sorted(msgs_results.keys())
            ]

    async def hmset_msg(self, key: str, data: dict):
        try:
            await self.connection.hmset(key, data)
        except Exception as _err:
            logger.error(f'Error with producing hmset msg {_err}')

    async def set_data(self, key: str, value: str, ttl_seconds: int = None):
        return await self.connection.set(
            name=key, value=value, ex=ttl_seconds or self.cache_ttl_seconds
        )

    async def delete_data(self, key):
        return await self.connection.delete(key) == 1

    async def delete_all_data(self):
        return await self.connection.flushdb() == 1

    async def publish(self, channel: str, msg: str):
        return await self.connection.publish(channel=channel, message=msg)

    async def subscribe(self, channel: str, timeout: int = 60):
        pubsub = self.connection.pubsub()
        await pubsub.subscribe(channel)
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=timeout)
            if msg:
                return {'channel': msg['channel'].decode(), 'data': msg['data'].decode()}

    async def close_connection(self):
        await self.connection.close()
