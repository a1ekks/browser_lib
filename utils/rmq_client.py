import json
from abc import ABC, abstractmethod

import aiormq
import httpx
from httpx import BasicAuth


class RabbitMqConfig:

    def __init__(self,
                 host: str,
                 port: int,
                 login: str = None,
                 password: str = None,
                 url: str = None,
                 virtualhost: str = None):

        self.password = password
        self.login = login
        self.port = port
        self.host = host
        self.url = url
        self.virtualhost = virtualhost
        self.management_api_url = None

        self.set_url()
        self.set_management_api_url()

    def to_dict(self):
        _data = self.__dict__
        _data.pop('url', None)
        return _data

    def set_management_api_url(self, management_port=15672):
        self.management_api_url = f'http://{self.host}:{management_port}/api'

    def set_url(self):
        """
        ampq url: 'amqp://user:password@ip_address:port/vhost'
        """
        if self.url:
            return
        auth = f'{self.login}:{self.password}@' if self.login and self.password else ''
        self.url = f'amqp://{auth}{self.host}:{self.port}/{self.virtualhost}'


class QueueClientAbstract(ABC):

    @abstractmethod
    async def init_connection(self):
        pass

    @abstractmethod
    async def close_connection(self):
        pass

    @abstractmethod
    async def get_queue_msg_count(self, queue):
        pass

    @abstractmethod
    async def create_queue(self, queue_name: str, ttl_hours=None):
        pass

    @abstractmethod
    async def get_now_from_queue(self, queue, debug=False) -> str:
        pass

    @abstractmethod
    async def check_queue_exists(self, queue_name: str):
        pass

    @abstractmethod
    async def handle_message_default_method(self, queue_message, ack=False):
        pass

    @abstractmethod
    async def get_awaiting_from_queue(self, queue: str = None, callback_ref=None, no_ack=True):
        pass

    @abstractmethod
    async def send_to_queue(self, msg: dict, queue: str = None):
        pass


async def init_rabbitmq_client_adapter(rabbitmq_config: dict, loop=None) -> QueueClientAbstract:
    rmq_config = RabbitMqConfig(**rabbitmq_config)
    rabbitmq = RabbitMqClient(rmq_config, loop)
    await rabbitmq.init_connection()

    return rabbitmq


class RabbitMqClient(QueueClientAbstract):

    def __init__(self,
                 rabbit_config: RabbitMqConfig,
                 loop,
                 logger=None,
                 default_queue: str = 'default'):
        self.default_queue = default_queue
        self.logger = logger
        self.loop = loop
        self.rabbit_config = rabbit_config

        self.connection = None
        self.channel = None

    async def __aenter__(self):
        if not self.connection:
            await self.init_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()

    async def init_connection(self):
        self.connection = await aiormq.connect(self.rabbit_config.url)
        self.channel = await self.connection.channel()

    async def close_connection(self):
        if not self.connection:
            return
        await self.channel.close()
        await self.connection.close()

    async def get_queue_msg_count(self, queue):
        if not self.connection.is_opened:
            await self.init_connection()
        queue = await self.channel.queue_declare(queue=queue, durable=True)
        return queue.message_count

    async def create_queue(self, queue_name: str, ttl_hours=None):
        # queue_is_exists = await self.check_queue_exists(queue_name)
        # if queue_is_exists:
        #     return

        # tt = await self.channel.basic_get(queue=queue_name)

        if ttl_hours:
            # TODO: need to check this legacy code from pika sync
            declared_queue = await self.channel.queue_declare(
                queue_name, durable=True, arguments={'x-message-ttl': 1000 * 60 * 60 * ttl_hours}
            )
        else:
            declared_queue = await self.channel.queue_declare(queue_name, durable=True)

        return declared_queue

    async def get_now_from_queue(self, queue, debug=False) -> str:
        if not self.connection.is_opened:
            await self.init_connection()
        result = await self.channel.basic_get(queue=queue)

        delivery, header, body, channel = result
        if delivery:
            if debug:
                print('\n'.join(
                    f'{flag}: {value}'
                    for flag, value in header.properties.flags.items()
                ))
            await self.channel.basic_ack(delivery_tag=delivery.delivery_tag)
            return body.decode('utf-8')

    async def check_queue_exists(self, queue_name: str):
        auth = BasicAuth(self.rabbit_config.login, self.rabbit_config.password)
        management_api_method = f'{self.rabbit_config.management_api_url}/queues'
        async with httpx.AsyncClient(timeout=30, verify=False, auth=auth)as client:
            try:
                result = await client.get(management_api_method)
                result_json = result.json()
            except Exception as _err:
                print(_err)
            else:
                return any((i for i in result_json if i.get('name') == queue_name))

    async def handle_message_default_method(self, queue_message, ack=False):
        message: dict = json.loads(queue_message.body.decode())
        if ack:
            await queue_message.channel.basic_ack(queue_message.delivery.delivery_tag)

        print(message)

        return message

    async def get_awaiting_from_queue(self, queue: str = None, callback_ref=None, no_ack=True):
        queue = await self.create_queue(queue or self.default_queue)
        await self.channel.basic_consume(
            queue.queue, (callback_ref or self.handle_message_default_method), no_ack=no_ack
        )

    async def send_to_queue(self, msg: dict, queue: str = None):
        message: bytes = json.dumps(msg).encode()

        queue = await self.create_queue(queue or self.default_queue)
        print(f'Sent msg: {msg}')
        await self.channel.basic_publish(message, routing_key=queue.queue)

        return msg.get('id')
