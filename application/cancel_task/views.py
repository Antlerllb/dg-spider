from flask import jsonify

from application.common import CLIENT_ERROR_CODE
from application.utils import request_scrapyd, format_json


def cancel():
    ok, msg = request_scrapyd('cancel')
    status_code = 200 if ok else CLIENT_ERROR_CODE
    return jsonify(format_json(not ok, msg)), status_code

