from flask import Blueprint

experts_blueprint = Blueprint("experts", __name__)

from . import routes
