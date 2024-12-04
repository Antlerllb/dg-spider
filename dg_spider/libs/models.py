# coding: utf-8
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, text
from sqlalchemy.dialects.mysql import CHAR, ENUM, MEDIUMTEXT, TEXT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Audit(Base):
    __tablename__ = 'audit'

    id = Column(Integer, primary_key=True, nullable=False, comment='自增id')
    user_id = Column(Integer, primary_key=True, nullable=False, comment='作者')
    website_id = Column(Integer, primary_key=True, nullable=False, index=True, comment='网站编号')
    task_id = Column(String(255), primary_key=True, nullable=False)
    status = Column(ENUM('APPROVED', 'REJECTED', 'IN_PROGRESS'), nullable=False, server_default=text("'IN_PROGRESS'"))
    code = Column(MEDIUMTEXT, nullable=False, comment='提交源码')
    commit_time = Column(DateTime, nullable=False, comment='提交时间')
    audit_time = Column(DateTime, comment='审核时间')
    created_time = Column(DateTime, comment='每当每行的数据被创建的时候更新现在的时间')
    updated_time = Column(DateTime, comment='触发器')


class Country(Base):
    __tablename__ = 'country'
    __table_args__ = {'comment': '国家信息表'}

    id = Column(Integer, primary_key=True, comment='自增ID')
    c_name = Column(TEXT, comment='国家名称')
    e_name = Column(VARCHAR(45), comment='英文名')
    created_time = Column(DateTime, comment='每当每行的数据被创建的时候更新现在的时间')
    updated_time = Column(DateTime, comment='更新时间')


class Language(Base):
    __tablename__ = 'language'

    id = Column(Integer, primary_key=True, comment='自增ID')
    name = Column(TEXT, comment='英文名')
    ISO_639_2 = Column(TEXT, comment='ISO 639-2 编码')
    ISO_639_1 = Column(TEXT, comment='ISO 639-1 编码')
    updated_time = Column(DateTime, comment='更新时间')
    created_time = Column(DateTime, comment='每当每行的数据被创建的时候更新现在的时间')


class Setting(Base):
    __tablename__ = 'setting'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), primary_key=True, nullable=False)
    category = Column(String(255))
    value = Column(String(255))
    label = Column(String(255))
    remark = Column(String(255))
    created_time = Column(DateTime)
    updated_time = Column(DateTime)


class Task(Base):
    __tablename__ = 'execute_task'

    id = Column(VARCHAR(255), primary_key=True, comment='uuid')
    argument = Column(JSON, comment='参数')
    log = Column(MEDIUMTEXT, comment='日志')
    created_time = Column(DateTime)
    updated_time = Column(DateTime)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'comment': '权限说明：\\n1 admin\\n10 管理员\\n'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(255), nullable=False)
    level = Column(Integer, nullable=False, server_default=text("'20'"))
    username = Column(VARCHAR(255), nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    grade = Column(Integer, nullable=False, server_default=text("'0'"), comment='0未知')
    enabled = Column(Integer, nullable=False, server_default=text("'0'"), comment='0禁用1启用')
    created_time = Column(DateTime)
    updated_time = Column(DateTime)


class Website(Base):
    __tablename__ = 'website'
    __table_args__ = {'comment': '0 待分配\\n5 待重写\\n10 开发中\\n20 审核中\\n30 审核通过\\n50 运行中\\n'}

    id = Column(Integer, primary_key=True, comment='id，自增，有索引')
    country_id = Column(ForeignKey('country.id'), index=True, server_default=text("'0'"), comment='外键：国家表的国家id')
    language_id = Column(ForeignKey('language.id'), index=True, server_default=text("'0'"), comment='外键：语言表的语言id')
    user_id = Column(ForeignKey('user.id', ondelete='RESTRICT', onupdate='RESTRICT'), index=True)
    url = Column(TEXT, comment='网站链接,http://开头')
    name = Column(TEXT, comment='爬虫名称')
    c_name = Column(TEXT, comment='中文名称')
    remark = Column(TEXT, comment='说明本网站在数据获取中的一些问题')
    level = Column(Integer, server_default=text("'999'"), comment='优先级别')
    status = Column(Enum('PENDING_ASSIGNMENT', 'PENDING_REWRITE', 'IN_PROGRESS', 'UNDER_REVIEW', 'APPROVED', 'RUNNING'), server_default=text("'PENDING_ASSIGNMENT'"))
    created_time = Column(DateTime, comment='每当每行的数据被创建的时候更新现在的时间')
    updated_time = Column(DateTime)

    country = relationship('Country')
    language = relationship('Language')
    user = relationship('User')


class News(Base):
    __tablename__ = 'news'
    __table_args__ = {'comment': '网站的新闻'}

    id = Column(Integer, primary_key=True, nullable=False, comment='新闻自身的id，自增')
    website_id = Column(ForeignKey('website.id'), index=True, comment='外键：新闻表网站地址id')
    request_url = Column(MEDIUMTEXT, nullable=False, comment='新闻的请求链接')
    response_url = Column(MEDIUMTEXT, comment='新闻网站的响应链接')
    category1 = Column(MEDIUMTEXT, comment='一级类别')
    category2 = Column(MEDIUMTEXT, comment='二级类别')
    title = Column(MEDIUMTEXT, comment='标题')
    abstract = Column(MEDIUMTEXT, comment='摘要')
    body = Column(MEDIUMTEXT, comment='正文')
    pub_time = Column(DateTime, comment='发布时间例2017-01-01 00:00:00,\\n没有发布时间的则为0000-00-00 00:00:00')
    cole_time = Column(DateTime, index=True, comment='爬虫时间  年-月-日 时:分:秒')
    images = Column(MEDIUMTEXT, comment='新闻图片列表，使用json的[]列表，没有则为NULL')
    language_id = Column(ForeignKey('language.id', ondelete='RESTRICT', onupdate='RESTRICT'), index=True, comment='外键：语音表的ID')
    md5 = Column(CHAR(32), primary_key=True, nullable=False, comment='8-24 bit')

    language = relationship('Language')
    website = relationship('Website')
