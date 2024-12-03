import hashlib


def str_to_md5(url):
    m = hashlib.md5()
    m.update(url.encode(encoding='utf-8'))
    return m.hexdigest()

def format_log(obj, msg:str=None, news_url:str=None, help_url:str=None, body:str=None):
    log = f"[{obj.__class__.__name__}]"
    if news_url: log += f" ({news_url})"
    if msg: log += f" ({msg})"
    if help_url: log += f" (help: {help_url})"
    if body: log += f"\n{body}"
    return log
