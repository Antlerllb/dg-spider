import logging

from typing import Optional, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dg_spider.libs.models import Setting
from dg_spider import my_cfg


class MysqlClient:
    _session_maker: sessionmaker = None

    @classmethod
    def setup(cls, db_config:Optional[dict]=my_cfg['mysql']):
        db_url = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?autocommit=true'.format(**db_config)
        engine = create_engine(db_url)
        cls._session_maker = sessionmaker(bind=engine)

    @classmethod
    def get_session(cls):
        if cls._session_maker is None:
            cls.setup()
        session = cls._session_maker()  # 创建一个新的会话
        return session



if __name__ == '__main__':
    with MysqlClient.get_session() as session, session.begin():
        # res = session.get(Language, 1727).name
        # print(res)
        session.add(Setting(name='fdsafadsf', value='fwea'))
        # session.commit()