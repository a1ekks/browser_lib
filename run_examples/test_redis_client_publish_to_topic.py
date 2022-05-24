import asyncio

from utils.redis_client import RedisCacheClientAsync


async def publish_cache(topic: str, msg: str):
    async with RedisCacheClientAsync(db_name='test') as redis_client:
        await redis_client.get_channels()
        res = await redis_client.publish(topic, msg)
        print(res)


if __name__ == '__main__':

    event_loop = asyncio.get_event_loop()
    # event_loop.run_until_complete(get_all_keys_by_template())

    # event_loop.run_until_complete(put_data('tt', '222222223'))
    # event_loop.run_until_complete(get_data('tt'))

    # event_loop.run_until_complete(subscribe_cache('test_url'))
    msg = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi in augue at quam congue tempor.
    Vestibulum ornare consequat elementum. Praesent vel felis diam. Suspendisse bibendum
    purus nibh, in cursus arcu cursus eget. Sed bibendum mattis efficitur.
    Curabitur ut elementum nisl. Orci varius natoque penatibus et magnis dis parturient
    montes, nascetur ridiculus mus.
    """
    event_loop.run_until_complete(publish_cache(
        topic='078e5b08-ea17-4426-b4ca-8f8c6c2a4b9a', msg=msg)
    )
