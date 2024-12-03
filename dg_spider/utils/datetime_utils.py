from datetime import datetime, timezone, timedelta

from dg_spider import my_cfg


time_zone_offset = timezone(timedelta(hours=my_cfg['time']['time_zone']))

# 毫秒时间戳 -> 日期
def stamp_to_date(timestamp: int):
    readable_date = datetime.fromtimestamp(timestamp / 1000, tz=time_zone_offset)
    return readable_date

# 日期 -> 毫秒时间戳
def date_to_stamp(iso_date_str: str):
    stamp = datetime.fromisoformat(iso_date_str).timestamp()
    return int(stamp * 1000)

def str_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=time_zone_offset)

# 获得当前毫秒级时间戳
def get_stamp():
    return int(datetime.now(time_zone_offset).timestamp() * 1000)

def get_date():
    return datetime.now(time_zone_offset)