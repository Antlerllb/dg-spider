from flask import jsonify
from application.utils import request_scrapyd, format_json
from application.common import CLIENT_ERROR_CODE


def execute_task():
    ok, msg = request_scrapyd('schedule')
    status_code = 200 if ok else CLIENT_ERROR_CODE
    return jsonify(format_json(not ok, msg)), status_code

