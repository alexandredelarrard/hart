from flask import Blueprint

closest_blueprint = Blueprint("closest", __name__)

from . import routes
