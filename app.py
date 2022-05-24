import logging

import fastapi

import config
from browser_lib.page_loader_manager import PageLoaderManager
from loader_task_api.views import loader_task
from utils.redis_client import redis_cache_client_adapter
from utils.rmq_client import QueueClientAbstract, init_rabbitmq_client_adapter


async def init_loader(app_config, logger):
    rabbitmq_queue_client: QueueClientAbstract = await init_rabbitmq_client_adapter(
        app_config.rabbitmq_config
    )
    redis_cache_client = await redis_cache_client_adapter(**app_config.redis_conf)

    page_loader_manager = PageLoaderManager(
        queue_client=rabbitmq_queue_client,
        cache_client=redis_cache_client,
        logger=logger
    )

    return page_loader_manager


api = fastapi.FastAPI()
api.include_router(loader_task.router)
logger = logging.getLogger('loader_api')


@api.on_event("startup")
async def startup_event():
    api.state.page_loader_manager = await init_loader(config, logger)
    logger.info('Added page_loader_manager...')
