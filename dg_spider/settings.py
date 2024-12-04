import datetime
import logging
import os

BOT_NAME = "dg_spider"

SPIDER_MODULES = ["dg_spider.spiders"]
NEWSPIDER_MODULE = "dg_spider.spiders"

# 日志文件名
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
LOG_FILE = f'logs/{current_date}.log'
if not os.path.exists(os.path.dirname(LOG_FILE)):
   os.makedirs(os.path.dirname(LOG_FILE))


# 日志过滤器
class ScrapyInfoFilter(logging.Filter):
   def filter(self, record):
      # 过滤掉 Scrapy 自带的 INFO 级别日志
      return not (record.levelname == 'INFO' and 'scrapy' in record.name)


LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s [%(levelname)s]: %(message)s'  # 日志格式
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'  # 日期格式


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'scrapy_filter': {
            '()': ScrapyInfoFilter,  # 绑定自定义过滤器
        },
    },
    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
            'datefmt': LOG_DATEFORMAT,
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'standard',
            'filters': ['scrapy_filter'],  # 应用过滤器
        }
    },
    'loggers': {
        'scrapy': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}



# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   # 初始化
   "dg_spider.middlewares.stats_middlewares.StatsInitMiddleware": 100,

   # item后处理
   "dg_spider.middlewares.response_middlewares.SpiderOutputMiddleware": 200,

   # 报错
   "dg_spider.middlewares.error_middlewares.SpiderErrorMiddleware": 300,

   # 审核
   "dg_spider.middlewares.audit_middlewares.AuditLangMiddleware": 510,
   "dg_spider.middlewares.audit_middlewares.AuditNewsMiddleware": 520,
   "dg_spider.middlewares.audit_middlewares.AuditFinalMiddleware": 580,

   # 统计
   "dg_spider.middlewares.stats_middlewares.StatsSummaryMiddleware": 800,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 代理
   "dg_spider.middlewares.proxy_middlewares.LabProxyMiddleware": 400,
   "dg_spider.middlewares.proxy_middlewares.TempProxyMiddleware": 410,

   # 请求
   "dg_spider.middlewares.request_middlewares.HeaderMiddlewares": 600,
   "dg_spider.middlewares.request_middlewares.FilterMiddleware": 610,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 审核
   "dg_spider.pipelines.audit_pipelines.AuditItemPipeline": 410,
   "dg_spider.pipelines.audit_pipelines.AuditLangPipeline": 420,
   "dg_spider.pipelines.audit_pipelines.AuditStatsPipeline": 430,

   # 定时
   "dg_spider.pipelines.schedule_pipelines.TimerPipeline": 500,

   # 持久化
   "dg_spider.pipelines.mysql_pipelines.MysqlNewsPipeline": 600,

   # 关闭
   "dg_spider.pipelines.schedule_pipelines.ShutdownPipeline": 800,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
