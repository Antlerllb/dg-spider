from pathlib import Path

from flask import jsonify, g, current_app, Response
from application.models import Website, Task, Audit
from application.utils import request_scrapyd, format_json, execute_bash, validate_common
from application.factory import my_cfg
from application.common import CLIENT_ERROR_CODE, USER_ERROR_CODE, DEPLOY_COMMAND

from dg_spider.utils.audit_utils import has_pylint_error, has_py_schema_error



def validate_run():
    if not g.argument['audit']['enabled']:
        spider: Website = Website.query.filter(Website.name == g.spider_name).one_or_none()
        if spider.status != 'RUNNING':
            return jsonify(format_json(True, '该爬虫未被部署，无法运行')), CLIENT_ERROR_CODE


def validate_audit():
    if g.argument['audit']['enabled']:
        audit: Audit = Audit.query.filter(Audit.id == g.argument['audit']['audit_id']).one_or_none()
        if audit is None:
            return jsonify(format_json(True, 'audit_id输入错误')), CLIENT_ERROR_CODE
        audit_temp_dir: Path = current_app.BASE_DIR.joinpath(my_cfg['flask']['temp_dir'])
        filename = audit_temp_dir.joinpath(f'{g.spider_name}.py')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(audit.code)
            pylint_error = has_pylint_error(f.name)
            py_schema_error = has_py_schema_error(f.name)
        filename.unlink()  # 删除文件
        if pylint_error:
            return jsonify(format_json(True, pylint_error)), USER_ERROR_CODE
        if py_schema_error:
            return jsonify(format_json(True, py_schema_error)), USER_ERROR_CODE

        g.code = audit.code


def deploy_audit_callback():
    ok, msg = request_scrapyd('addversion')
    status_code = 200 if ok else CLIENT_ERROR_CODE
    return format_json(not ok, msg), status_code


def deploy_audit():
    if g.argument['audit']['enabled']:
        base_dir: Path = current_app.BASE_DIR
        filename = base_dir.joinpath(my_cfg['scrapy']['project']).joinpath(f'{g.spider_name}.py')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(g.code)
        return Response(execute_bash(DEPLOY_COMMAND, base_dir, success_callback=deploy_audit_callback),
                        mimetype='text/event-stream', status=200)
