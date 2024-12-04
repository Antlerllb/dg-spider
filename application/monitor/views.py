from flask import jsonify

from application.common import CLIENT_ERROR_CODE
from application.utils import request_scrapyd, format_json


def get_log():
    ok, msg = request_scrapyd('log')
    status_code = 200 if ok else CLIENT_ERROR_CODE
    return jsonify(format_json(not ok, msg)), status_code


def get_status():
    ok, msg = request_scrapyd('status')
    status_code = 200 if ok else CLIENT_ERROR_CODE
    return jsonify(format_json(not ok, msg)), status_code
