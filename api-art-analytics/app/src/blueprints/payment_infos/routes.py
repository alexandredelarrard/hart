from flask import request, jsonify
from sqlalchemy import desc
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.extensions import db
from src.schemas.payment import PaymentTrack
import logging

from . import payment_blueprint

@payment_blueprint.route('/new-payment', methods=['POST'])
@jwt_required()
def new_payment():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get("user_id")
        return jsonify({'message': 'Activity logged successfully'}), 201
       

@payment_blueprint.route('/user-payment-infos', methods=['GET'])
@jwt_required()
def user_payment_infos():

    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if user_id:
            results = PaymentTrack.query.filter_by(user_id=user_id).order_by(desc(PaymentTrack.plan_start_date)).all()
            list_results= [item.to_dict() for item in results]
            logging.info(list_results)
            return jsonify({"results": list_results}), 200
        else:
            return jsonify({"error": 'missing user ID'}), 400
    
    else:
        return jsonify({"error": 'method only GET'}), 500
