from flask import Blueprint

chatbot_blueprint = Blueprint("chatbot", __name__)

from . import routes
