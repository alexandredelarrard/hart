from flask import request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.extensions import db
from src.schemas.activity import ActivityLog

from . import activity_blueprint

@activity_blueprint.route('/log-activity', methods=['POST'])
@jwt_required()
def log_activity():

    if request.method == 'POST':

        data = request.get_json()
        user_id = data.get("user_id")
        user_email = get_jwt_identity()['email']
        activity_type = data.get('activity_type')
        activity_details = data.get('activity_details')

        if not activity_type:
            return jsonify({'error': 'Activity type is required'}), 400

        new_log = ActivityLog(
            user_id=user_id,
            user_email=user_email,
            activity_type=activity_type,
            activity_details=activity_details,
            activity_timestamp=datetime.now()
        )

        try:
            db.session.add(new_log)
            db.session.commit()
            return jsonify({'message': 'Activity logged successfully'}), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to log activity', 'details': str(e)}), 500