from flask import Blueprint

search_db_blueprint = Blueprint('search_db', __name__)

from . import routes