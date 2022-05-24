from logging import getLogger, INFO, LoggerAdapter, basicConfig


class WorkerLoggerAdapter(LoggerAdapter):

    def process(self, msg, kwargs):
        worker_id = kwargs.pop('worker_id', self.extra['worker_id'])
        return '[%s] %s' % (worker_id, msg), kwargs


def configure_worker_logger(name, logger_kwargs: dict = None):
    basicConfig(
        level=INFO,
        format='%(asctime)s - %(levelname)s - %(name)s.%(module)s: %(message)s',
        datefmt='%m-%d-%y %H:%M:%S'
    )

    if logger_kwargs:
        return WorkerLoggerAdapter(getLogger(name), logger_kwargs)

    return getLogger(name)
