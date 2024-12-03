from flask import Blueprint
from . import views

monitor_bp = Blueprint("monitor", __name__)
monitor_bp.add_url_rule("/get_log", view_func=views.get_log, methods=["post"])
monitor_bp.add_url_rule("/get_status", view_func=views.get_status, methods=["post"])




