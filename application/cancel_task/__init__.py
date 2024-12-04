from flask import Blueprint
from application import utils
from . import views

cancel_bp = Blueprint("cancel", __name__)

cancel_bp.before_request(utils.validate_common)

cancel_bp.add_url_rule("/cancel", view_func=views.cancel, methods=["post"])
