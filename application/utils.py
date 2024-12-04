import json
import os
import subprocess
from pathlib import Path

import requests
from flask import jsonify, g, current_app, request

from application.common import CLIENT_ERROR_CODE
from application.models import Website, Task
from dg_spider import my_cfg
from dg_spider.utils.audit_utils import has_json_schema_error


def format_json(has_error: bool, msg: str):
    return {'has_error': has_error, 'msg': msg}


def request_scrapyd(api:str):
    flask_cfg, scrapy_cfg = my_cfg['flask'], my_cfg['scrapy']
    if api == 'schedule':
        url = '{url}/{api}.json'.format(**scrapy_cfg, api=api)
        data = {'project': scrapy_cfg['project'], 'spider': g.spider_name, 'jobid': g.task_id, 'task_id': g.task_id}
        resp = requests.post(url, data=data).json()
        msg = '启动成功' if resp['status'] == 'ok' else resp['message']
        return resp['status'] == 'ok', msg
    elif api == 'cancel':
        url = '{url}/{api}.json'.format(**scrapy_cfg, api=api)
        data = {'project': scrapy_cfg['project'], 'job': g.task_id}
        resp = requests.post(url, data=data).json()
        msg = '正在取消' if resp['status'] == 'ok' else resp['message']
        return resp['status'] == 'ok', msg
    elif api == 'status':
        url = '{url}/{api}.json'.format(**scrapy_cfg, api=api)
        data = {'job': g.task_id}
        resp = requests.post(url, data=data).json()
        msg = resp['currstate'] if resp['status'] == 'ok' else resp['message']
        return resp['status'] == 'ok', msg
    elif api == 'log':
        url = '{url}/logs/{project}/{spider_name}/{task_id}.log'.format(
            **scrapy_cfg, spider_name=g.spider_name, task_id=g.task_id)
        resp = requests.get(url)
        return resp.status_code == 200, resp.text


def execute_bash(bash_command, cwd, env=None):
    process = subprocess.Popen(
        bash_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env if env else os.environ.copy(),
        cwd=cwd,
    )
    stdout_lines, stderr_lines = [], []
    while True:
        return_code = process.poll()
        output = process.stdout.readline()
        if output:
            stdout_lines.append(output.strip())
        error = process.stderr.readline()
        if error:
            stderr_lines.append(error.strip())
        if return_code is not None and not output and not error:
            break
    return stdout_lines, stderr_lines


def validate_common():
    if not request.is_json:
        return jsonify(format_json(True, '请求格式必须为JSON')), CLIENT_ERROR_CODE
    flask_args_schema_error = has_json_schema_error(request.json, 'flask_args')
    if flask_args_schema_error:
        return jsonify(format_json(True, f'请求参数格式错误：{flask_args_schema_error}')), CLIENT_ERROR_CODE
    task = Task.query.filter(Task.id == request.json['task_id']).one_or_none()
    if task is None:
        return jsonify(format_json(True, 'task_id输入错误')), CLIENT_ERROR_CODE
    spider_args_schema_error = has_json_schema_error(task.argument, 'spider_args')
    if spider_args_schema_error:
        return jsonify(format_json(True, f'爬虫参数格式错误：{spider_args_schema_error}')), CLIENT_ERROR_CODE
    spider: Website = Website.query.filter(Website.id == task.argument['spider']['website_id']).one_or_none()
    if spider is None:
        return jsonify(format_json(True, 'website_id输入错误')), CLIENT_ERROR_CODE

    g.task_id = request.json['task_id']
    g.argument = task.argument
    g.spider_name = spider.name
