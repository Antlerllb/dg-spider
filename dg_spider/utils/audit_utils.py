import ast
from io import StringIO
import cld2
import requests
from pylint import lint
from ast2json import ast2json
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError
import importlib.resources as pkg_resources
from pylint.reporters.text import TextReporter
from dg_spider.utils.io_utils import read_json, get_path, read_text


def has_json_schema_error(json_data: dict, schema_name):
    target_schema = read_json(f'json_schema/{schema_name}.json')
    common_schema_path = 'json_schema/common.json'
    try:
        with pkg_resources.path(*get_path(common_schema_path)) as common_schema_datafile:
            resolver = RefResolver(base_uri=common_schema_datafile.as_uri(), referrer=read_json(common_schema_path))
            validate(instance=json_data, schema=target_schema, resolver=resolver)
            return None
    except ValidationError as e:
        msg = f'{e.args[0]}'
        if e.schema.get('description'):
            msg += f"，{e.schema.get('description')}"
        return msg


def has_pylint_error(py_path):
    pylint_output = StringIO()  # Custom open stream
    reporter = TextReporter(pylint_output)
    with pkg_resources.path(*get_path(py_path)) as data_file:
        with pkg_resources.path(*get_path('config/.pylintrc')) as config_file:
            result = lint.Run([f'--rcfile={str(config_file)}', str(data_file)], reporter=reporter, exit=False)
            if result.linter.msg_status != 0:
                return pylint_output.getvalue()


def has_lang_error(text, lang_iso, second_max_threshold, detect_exclude_list):
    lang_detect_info = {'has_error': False}
    try:
        is_reliable, text_bytes_found, details = cld2.detect(text)
        first_lang_iso, first_confidence = details[0][1], details[0][2]
        second_lang_iso, second_confidence = details[1][1], details[1][2]
        error_reason = []
        if lang_iso not in detect_exclude_list:  # 常规语言
            if lang_iso not in first_lang_iso:  # not in: 因为有时real_lan_iso是"zh_cn"
                error_reason.append('id标注错误')
            if second_confidence > second_max_threshold:
                error_reason.append(f'第二候选置信度高于{second_max_threshold}')
        else:  # 冷门语言
            if first_lang_iso != 'un':
                error_reason.append('冷门语言标注错误')
        if error_reason:
            lang_detect_info['has_error'] = True
            lang_detect_info['first_lang_iso'] = first_lang_iso
            lang_detect_info['first_confidence'] = first_confidence
            lang_detect_info['second_lang_iso'] = second_lang_iso
            lang_detect_info['second_confidence'] = second_confidence
            lang_detect_info['error_reason'] = '，'.join(error_reason)
        return lang_detect_info
    except Exception as e:
        error_text = str(e.args[0])
        if 'UTF-8' in error_text:
            lang_detect_info['error_reason'] = f'未处理utf-8编码无效问题：{error_text}'
        else:
            lang_detect_info['error_reason'] = error_text
        lang_detect_info['has_error'] = True
        return lang_detect_info


def has_py_schema_error(py_path):
    ast_node = ast2json(ast.parse(read_text(py_path)))
    res = has_json_schema_error(ast_node, 'py_ast')
    return res


def is_url_accessible(url):
    try:
        response = requests.head(url, timeout=3)  # 使用 HEAD 请求，效率较高
        return response.status_code < 400   # 2xx 和 3xx 状态码表示可达
    except requests.RequestException as e:
        return False
