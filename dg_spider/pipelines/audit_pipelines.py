import json
from typing import Optional

from pylint import modify_sys_path
from scrapy.exceptions import DropItem, CloseSpider

from dg_spider import my_cfg
from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import Language, Setting
from dg_spider.pipelines.base_pipelines import MysqlPipeline
from dg_spider.utils.audit_utils import has_json_schema_error, has_lang_error
from dg_spider.utils.format_utils import format_log


class AuditItemPipeline:
    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and spider.args['audit']['enabled'] and isinstance(item, NewsItem):
            error = has_json_schema_error(dict(item), 'news')
            if error:
                spider.logger.error(format_log(self, error, news_url=item['request_url']))
                spider.crawler.stats.inc_value('audit_item_error_count')
                return None
        return item


class AuditLangPipeline(MysqlPipeline):
    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and spider.args['audit']['enabled'] and isinstance(item, NewsItem):
            # 统计信息
            spider.crawler.stats.inc_value('audit_lang_total_count')
            # 开始检测
            lang_detect_exclude_list = json.loads(self.session.query(Setting).filter(Setting.name == 'lang_detect_exclude_list').first().value)
            lang_second_max_threshold = float(self.session.query(Setting).filter(Setting.name == 'lang_second_max_threshold').first().value)
            text_to_detect = '\n'.join([item['title'], item['body']])
            lang_record = self.session.query(Language).filter(Language.id==item['language_id']).first()
            if lang_record is not None:
                lang_info = has_lang_error(text_to_detect, lang_record.ISO_639_1, lang_second_max_threshold, lang_detect_exclude_list)
                if lang_info['has_error']:
                    if 'utf-8' in lang_info.get('error_reason'):  # 编码错误
                        error_list = [
                            f'报错原因：{lang_info["error_reason"]}。'
                        ]
                    else:  # 常规错误
                        error_list = [
                            f'报错原因：{lang_info["error_reason"]}',
                            f'你的标注：{lang_record.ISO_639_1}, language_id={item["language_id"]}',
                            f'检测结果第一候选：{lang_info["first_lang_iso"]}，置信度为[{lang_info["first_confidence"]}/100]。',
                            f'检测结果第二候选：{lang_info["second_lang_iso"]}，置信度为[{lang_info["second_confidence"]}/100]。',
                        ]
                    if '冷门语言' in lang_info.get('error_reason'):  # 冷门语言标注错误
                        error_list.append(f'备注：{lang_info["lan_id"]}为冷门语言，cld2判定为un（未知）为正常现象。如果判定为其他语言，说明你标注错了。')
                    spider.crawler.stats.inc_value('audit_lang_error_count')
                    spider.logger.error(format_log(self, body='\n'.join(error_list)))
                    return None
            else:
                error_list = [
                    f'报错原因：未找到language_id',
                    f'你的标注：language_id={item["language_id"]}',
                ]
                spider.crawler.stats.inc_value('audit_lang_error_count')
                spider.logger.error(format_log(self, body='\n'.join(error_list)))
                return None
        return item
