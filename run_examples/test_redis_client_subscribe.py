import asyncio
import random

from utils.redis_client import RedisCacheClientAsync


async def _subscribe_cache(topic: str):
    async with RedisCacheClientAsync(db_name='test') as redis_client:
        res = await redis_client.subscribe(topic)
        print(res)


async def subscribe_cache(topic: str, subscriber_name: str = None):
    async with RedisCacheClientAsync(db_name='test') as redis_client:
        wait_for = random.randint(5, 10)
        await asyncio.sleep(wait_for)
        if subscriber_name:
            print(f'Init for {subscriber_name} {wait_for}...')
        res = await redis_client.subscribe(topic)
        print(f'{subscriber_name}: {res}')


async def init_some_subscribers(topic: str):
    tasks = []
    for sub in range(2):
        _task = asyncio.create_task(subscribe_cache(topic, f'subscriber_{sub}'))
        tasks.append(_task)

    await asyncio.gather(*tasks)


if __name__ == '__main__':

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(init_some_subscribers('test_url'))
