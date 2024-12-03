import logging
from dg_spider.settings import LOG_FORMAT, LOG_DATEFORMAT, LOG_LEVEL, LOG_FILE


class ScrapyInfoFilter(logging.Filter):
    def filter(self, record):
        # 过滤掉 Scrapy 自带的 INFO 级别日志
        return not (record.levelname == 'INFO' and 'scrapy' in record.name)

def setup_log_handler(handler: logging.Handler):
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATEFORMAT)
    handler.setFormatter(formatter)
    return handler

def get_external_logger():
    my_logger = logging.getLogger()
    my_logger.setLevel(LOG_LEVEL)
    if not any(isinstance(handler, logging.StreamHandler) for handler in my_logger.handlers):
        my_logger.addHandler(setup_log_handler(logging.StreamHandler()))
    if not any(isinstance(handler, logging.FileHandler) for handler in my_logger.handlers):
        my_logger.addHandler(setup_log_handler(logging.FileHandler(LOG_FILE)))
    return my_logger
