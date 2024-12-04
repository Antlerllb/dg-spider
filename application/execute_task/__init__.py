from flask import Blueprint
from application import utils
from . import views
from . import before_rq

execute_task_bp = Blueprint("execute_task", __name__)

execute_task_bp.before_request(utils.validate_common)
execute_task_bp.before_request(before_rq.validate_run)
execute_task_bp.before_request(before_rq.validate_audit)
execute_task_bp.before_request(before_rq.deploy_audit)

execute_task_bp.add_url_rule("/execute", view_func=views.execute_task, methods=["post"])
