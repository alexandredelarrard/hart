from flask import request, jsonify
from . import closest_blueprint
from celery.result import AsyncResult
from src.backend.tasks import process_request
import logging


@closest_blueprint.route('/process', methods=['POST'])
def process():

    if 'file' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Missing file or text"}), 400

    image = request.files['file']
    text = request.form['text']

    # Read the file content
    image = image.read()

    if not image and not text:
        return jsonify({"error": "Missing image and text"}), 400

    task = process_request.apply_async(args=[image, text])

    return jsonify({"task_id": task.id}), 202

@closest_blueprint.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result,
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
        }
    return jsonify(response), 200