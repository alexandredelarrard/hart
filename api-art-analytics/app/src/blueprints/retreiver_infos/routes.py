from flask import request, jsonify
from typing import List
from flask_cors import  cross_origin
from src.schemas.user import AllItems
from src.extensions import db

from . import infos_blueprint
from src.extensions import front_server

# =============================================================================
# additonal infos
# =============================================================================
@infos_blueprint.route('/ids_infos', methods=['POST'])
@cross_origin(origins=front_server)
def post_ids_infos():

    if request.method == 'POST':
        data = request.get_json()
        ids = data.get('ids')

        if not ids:
            return jsonify({"error": "No IDs provided"}), 400
        
        if isinstance(ids, List):
            try:
                result = AllItems.query.filter(AllItems.ID_UNIQUE.in_(ids)).all()
                output = [item.to_dict() for item in result]
                return jsonify(output), 200
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
        else:
            return jsonify({"error": 'ids does not have the expected format'}), 400
