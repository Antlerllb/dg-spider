import json
import importlib.resources as pkg_resources


def get_path(path):
    parts = path.split('/')
    file_name = parts[-1]  # 提取文件名
    if len(parts) == 1:
        resource_path = "dg_spider.resources"
    else:
        resource_path = "dg_spider.resources." + ".".join(parts[:-1])
    resource_path = resource_path.rstrip('.')  # 去除可能的末尾点
    return resource_path, file_name

def read_json(path):
    resource_path, file_name = get_path(path)
    with pkg_resources.path(resource_path, file_name) as datafile:
        with open(datafile, 'r', encoding='utf-8') as f:
            return json.load(f)

def read_text(path):
    resource_path, file_name = get_path(path)
    with pkg_resources.path(resource_path, file_name) as datafile:
        with open(datafile, 'r', encoding='utf-8') as f:
            return f.read()
