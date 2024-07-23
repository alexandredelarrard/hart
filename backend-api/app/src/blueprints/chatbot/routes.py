import os

from flask import request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from . import chatbot_blueprint

from src.extensions import config, context
from src.extensions import front_server
from src.schemas.results import CloseResult
from src.extensions import db

if os.getenv("FLASK_ENV") == "flask_worker":
    from src.gpt_caller import GptChat

    step_gpt = GptChat(config=config, context=context, methode="open_ai")


@chatbot_blueprint.route("/chatbot", methods=["POST"])
@cross_origin(origins=front_server)
@jwt_required()
def designation_chat():

    if request.method == "POST":
        data = request.get_json()
        task_id = data.get("task_id")
        art_pieces = data.get("art_pieces")

        if not art_pieces:
            return jsonify({"error": "No question / art piece provided"}), 400

        # retreive llm_info
        llm_results = step_gpt.get_llm_result(art_pieces)

        result = CloseResult.query.filter_by(task_id=task_id).first_or_404()
        if result:
            result.llm_result = str(llm_results)
            db.session.commit()

        if len(llm_results) != 0:
            return jsonify({"result": llm_results}), 200
        else:
            return jsonify({"error": "could not write designation "}), 400
