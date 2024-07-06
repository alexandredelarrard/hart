from flask import Blueprint

authorization_blueprint = Blueprint("authorization", __name__)

from . import routes
