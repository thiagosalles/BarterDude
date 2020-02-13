from aiohttp import web
from abc import ABCMeta, abstractmethod
from barterdude import BarterDude
from asyncworker.rabbitmq.message import RabbitMQMessage


class BaseHook(metaclass=ABCMeta):
    @abstractmethod
    async def on_success(self, message: RabbitMQMessage):
        '''Called after successfuly consumed the message'''

    @abstractmethod
    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        '''Called when fails to consume the message'''

    @abstractmethod
    async def before_consume(self, message: RabbitMQMessage):
        '''Called before consuming the message'''


class HttpHook(BaseHook):
    def __init__(self, barterdude: BarterDude, path: str):
        barterdude.add_endpoint(
            routes=[path],
            methods=["GET"],
            hook=self
        )

    async def __call__(self, req: web.Request = None):
        raise NotImplementedError

    async def on_success(self, message: RabbitMQMessage):
        raise NotImplementedError

    async def on_fail(self, message: RabbitMQMessage, error: Exception):
        raise NotImplementedError

    async def before_consume(self, message: RabbitMQMessage):
        raise NotImplementedError
