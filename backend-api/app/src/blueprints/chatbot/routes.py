from flask import request, jsonify
from . import chatbot_blueprint
from src.backend.tasks import chat_request
import logging


@chatbot_blueprint.route('/chatbot', methods=['POST'])
def designation_chat():

    if request.method == 'POST':
        data = request.get_json()
        art_pieces = data.get('art_pieces')
        question = data.get('question')
    
        if not question or not art_pieces:
            return jsonify({"error": "No question / art piece provided"}), 400

        task = chat_request.apply_async(args=[art_pieces, question])

        return jsonify({"task_id": task.id}), 202
