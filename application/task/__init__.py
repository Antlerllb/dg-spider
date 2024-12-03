from flask import Blueprint
from . import views


task_bp = Blueprint("task", __name__)
task_bp.add_url_rule("/execute", view_func=views.execute_task, methods=["post"])

