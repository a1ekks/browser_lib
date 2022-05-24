import asyncio

from utils.redis_client import RedisCacheClientAsync


async def get_all_keys_by_template(def_template='*'):
    async with RedisCacheClientAsync() as redis_client:
        async for res in redis_client.get_keys_by_template(def_template):
            print(res)


async def put_data(key, value):
    async with RedisCacheClientAsync() as redis_client:
        await redis_client.set_data(key=key, value=value)


async def get_data(key):
    async with RedisCacheClientAsync(db_name='test') as redis_client:
        res = await redis_client.get_data(key)
        print(res)


async def foo():
    print('starting foo')
    r = 0
    while True:
        print(r)
        r += 1
        if r > 42:
            return 42


async def bar():
    await asyncio.sleep(10)
    return 'ttt'


async def run_tt():
    task = asyncio.create_task(foo())
    done, pending = await asyncio.wait({task})

    b = await bar()
    print(b)

    if task in done:
        print(task.result())

if __name__ == '__main__':

    event_loop = asyncio.get_event_loop()
    # event_loop.run_until_complete(get_all_keys_by_template())

    # event_loop.run_until_complete(put_data('tt', '222222223'))
    # event_loop.run_until_complete(get_data('tt'))

    event_loop.run_until_complete(run_tt())
