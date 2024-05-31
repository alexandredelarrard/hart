from flask import Blueprint

infos_blueprint = Blueprint('infos', __name__)

from . import routes