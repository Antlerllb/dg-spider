from flask import Blueprint
from application import utils
from . import views
from . import before_rq

task_bp = Blueprint("task", __name__)

task_bp.before_request(utils.validate_common)
task_bp.before_request(before_rq.validate_run)
task_bp.before_request(before_rq.validate_audit)
task_bp.before_request(before_rq.deploy_audit)

task_bp.add_url_rule("/execute", view_func=views.execute_task, methods=["post"])
