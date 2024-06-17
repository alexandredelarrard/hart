from flask import request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from . import expert_blueprint
from src.schemas.experts import Experts
from src.extensions import db
from src.extensions import front_server

@expert_blueprint.route('/get-experts-close', methods=['POST'])
@cross_origin(origins=front_server)
@jwt_required()
def get_close_expert():
    if request.method == 'POST':
        data = request.get_json()
        longitude = data.get('longitude')
        latitude = data.get('longitude')
        
        if longitude and latitude:
            return jsonify({'message': 'Your password has been updated.'}), 200
       
        return jsonify({'error': 'Invalid token'}), 400