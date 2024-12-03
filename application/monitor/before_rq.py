from application.utils import validate_common
from application.monitor import monitor_bp


@monitor_bp.before_request
def before_request():
    validate_common()


