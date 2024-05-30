from flask import request, jsonify
from . import closest_blueprint
from src.backend.tasks import process_request

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