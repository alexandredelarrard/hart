from flask import request, jsonify
from . import chatbot_blueprint
import os 
from src.extensions import config, context

if os.getenv('FLASK_ENV') == 'flask_worker':
    from src.transformers.GptChat import GptChat
    step_gpt = GptChat(config=config, context=context, 
                        methode="open_ai")

@chatbot_blueprint.route('/chatbot', methods=['POST'])
def designation_chat():

    if request.method == 'POST':
        data = request.get_json()
        art_pieces = data.get('art_pieces')
    
        if not art_pieces:
            return jsonify({"error": "No question / art piece provided"}), 400

        results, _ = step_gpt.get_answer(art_pieces=art_pieces[:48])
        return jsonify({"result": results}), 202
