from flask import Blueprint
from flask import request

api = Blueprint('api', __name__, url_prefix='/api/quiz')
user_bp = Blueprint('userRoutes', __name__, url_prefix='/api/user')
analyize = Blueprint('analytics', __name__, url_prefix='/api/analytics')

def check_json_request():
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    return None

from . import routes
# from . import quiz_routesd
from . import user_routes
from . import analytics
