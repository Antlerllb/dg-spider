from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import Setting, Website, Audit
from dg_spider.libs.mysql_client import MysqlClient
from dg_spider.middlewares.base_middlewares import BaseStatsMiddleware
from dg_spider.utils.datetime_utils import get_date
from dg_spider.utils.format_utils import format_log


class AuditLangMiddleware(BaseStatsMiddleware):
    def spider_closed(self, spider: BaseSpider):
        if spider.args['audit']['enabled']:
            lang_error_max_threshold = float(self.session.query(Setting).filter(Setting.name == 'lang_error_max_threshold').first().value)
            lang_error_rate = float(self.stats.get_value('audit_lang_error_count')/(self.stats.get_value('audit_lang_total_count')+1))
            if lang_error_rate > lang_error_max_threshold:
                self.stats.set_value('is_audit_passed', False)
                msg = f'语言检测失败，错误率为{lang_error_rate}，超过{lang_error_max_threshold}'
                spider.logger.error(format_log(self, msg))
            else:
                msg = f'语言检测通过，错误率为{lang_error_rate}，小于{lang_error_max_threshold}'
                spider.logger.info(format_log(self, msg))


class AuditNewsMiddleware(BaseStatsMiddleware):
    def spider_closed(self, spider: BaseSpider):
        if spider.args['audit']['enabled']:
            minimum_news_count = int(self.session.query(Setting).filter(Setting.name == 'minimum_news_count').first().value)
            audit_success_count = self.stats.get_value('audit_success_count')
            if audit_success_count < minimum_news_count:
                self.stats.set_value('is_audit_passed', False)
                msg = f'新闻数量较少，新闻量为{audit_success_count}，小于{minimum_news_count}'
                spider.logger.error(format_log(self, msg))


class AuditFinalMiddleware(BaseStatsMiddleware):
    def spider_closed(self, spider: BaseSpider):
        if spider.args['audit']['enabled']:
            # 打印日志
            if self.stats.get_value('is_audit_passed'):
                spider.logger.info(format_log(self, '终审通过'))
            else:
                spider.logger.error(format_log(self, '终审不通过'))
            # 持久化
            if spider.args['audit']['mysql_enabled']:
                website_id, audit_id = spider.args['spider']['website_id'], spider.args['audit']['audit_id']
                with MysqlClient.get_session() as session, session.begin():
                    website_to_update = session.query(Website).filter(Website.id == website_id).first()
                    audit_to_update = session.query(Audit).filter(Audit.id == audit_id).first()
                    if self.stats.get_value('is_audit_passed'):
                        website_to_update.status = audit_to_update.result = 'RUNNING'
                    else:
                        website_to_update.status = 'IN_PROGRESS'
                        audit_to_update.result = 'REJECTED'
                    audit_to_update.audit_time = get_date()
