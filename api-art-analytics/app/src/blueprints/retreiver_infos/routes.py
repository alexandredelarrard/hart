from flask import request, jsonify
import logging
from flask_cors import  cross_origin
from src.schemas.user import AllItems
from src.extensions import db

from . import infos_blueprint
from src.extensions import front_server

# =============================================================================
# authentification
# =============================================================================
@infos_blueprint.route('/ids_infos', methods=['GET'])
@cross_origin(origins=front_server)
def get_ids_infos():
    if request.method == 'GET':
        ids = request.args.get('ids')
        if not ids:
            return jsonify({"error": "No IDs provided"}), 400

        try:
            result = AllItems.query.filter(AllItems.ID_UNIQUE.in_(ids.split(','))).all()
            output = [item.to_dict() for item in result]
            return jsonify(output), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
