import asyncio

from utils.rmq_client import RabbitMqClient, RabbitMqConfig


async def get_queue_count(queue_name, loop):
    async with RabbitMqClient(RabbitMqConfig(**rabbitmq_config), loop) as rmq:
        res = await rmq.get_queue_msg_count(queue_name)
        print(queue_name, res)


async def rmq_create_queue(queue_name, loop):
    async with RabbitMqClient(RabbitMqConfig(**rabbitmq_config), loop) as rmq:
        res = await rmq.create_queue(queue_name)
        print(queue_name, res)


async def produce_msgs_to_queue(messages: list, queue_name='default', loop=None):
    async with RabbitMqClient(RabbitMqConfig(**rabbitmq_config), loop) as rmq:
        for msg in messages:
            await rmq.send_to_queue(msg, queue_name)


async def get_message(queue_name, loop):
    async with RabbitMqClient(RabbitMqConfig(**rabbitmq_config), loop) as rmq:
        message = await rmq.get_now_from_queue(queue_name)
        print(message)


if __name__ == '__main__':
    rabbitmq_config = {
        'host': '127.0.0.1',
        'port': 5672,
        'login': 'browserlib',
        'password': 'browserlib123',
        'virtualhost': 'browser_parsing'
    }

    event_loop = asyncio.get_event_loop()
    queue_name = 'default'
    event_loop.run_until_complete(
        produce_msgs_to_queue([{"message": i} for i in range(100)], queue_name, event_loop)
    )
