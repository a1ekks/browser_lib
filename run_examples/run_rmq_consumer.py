import asyncio

from utils.rmq_client import init_rabbitmq_client_adapter


if __name__ == '__main__':
    rabbitmq_config = {
        'host': '127.0.0.1',
        'port': 5672,
        'login': 'browserlib',
        'password': 'browserlib123',
        'virtualhost': 'browser_parsing'
    }

    event_loop = asyncio.get_event_loop()

    rmq = event_loop.run_until_complete(init_rabbitmq_client_adapter(rabbitmq_config, event_loop))
    queue_name = 'test1'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rmq.get_awaiting_from_queue(queue_name))
    loop.run_forever()
