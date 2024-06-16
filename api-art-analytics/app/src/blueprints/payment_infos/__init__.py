from flask import Blueprint

payment_blueprint = Blueprint('payment', __name__)

from . import routes