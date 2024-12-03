from typing import Optional
from sqlalchemy.orm import Session

from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.mysql_client import MysqlClient


class MysqlPipeline:
    session: Optional[Session]

    def __init__(self):
        self.session = MysqlClient.get_session()

    def close_spider(self, spider: BaseSpider):
        self.session.close()
