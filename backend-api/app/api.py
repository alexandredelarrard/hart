from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import logging
from celery import Celery
from .tasks import process_request

app = Blueprint('api', __name__)
CORS(app)  # Enable CORS for the entire app

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for the entire app
    app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

    from .api import app as api_blueprint
    app.register_blueprint(api_blueprint)

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

@app.route('/process', methods=['POST'])
def process():

    if 'file' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Missing file or text"}), 400

    image = request.files['file']
    text = request.form['text']

    # Read the file content
    image = image.read()

    if not image or not text:
        return jsonify({"error": "Missing image or text"}), 400

    task = process_request.apply_async(args=[image, text])
    return jsonify({"task_id": task.id}), 202

if __name__ == '__main__':
    flask_app = create_app()
    celery = make_celery(app)
    flask_app.run(host='0.0.0.0', port=5000)