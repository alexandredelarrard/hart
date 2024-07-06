from flask import Blueprint

activity_blueprint = Blueprint("activity", __name__)

from . import routes
