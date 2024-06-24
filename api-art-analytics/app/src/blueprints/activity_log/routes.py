from flask import request, jsonify
from sqlalchemy import func, case, cast, Date
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.extensions import db
from src.schemas.activity import ActivityLog, Newsletter

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
        geolocalisation = data.get('geolocation')
        machineSpecs = data.get('machineSpecs')

        if not activity_type:
            return jsonify({'error': 'Activity type is required'}), 400

        new_log = ActivityLog(
            user_id=user_id,
            user_email=user_email,
            activity_type=activity_type,
            activity_details=activity_details,
            activity_timestamp=datetime.now(),
            geolocalisation=str(geolocalisation),
            machinespecs=str(machineSpecs)
        )

        try:
            db.session.add(new_log)
            db.session.commit()
            return jsonify({'message': 'Activity logged successfully'}), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to log activity', 'details': str(e)}), 500
        

@activity_blueprint.route('/add-newsletter', methods=['POST'])
def add_newsletter():

    data = request.get_json()
    email = data.get("email")

    email_news = Newsletter.query.filter_by(email=email).first()

    if email_news:
        return jsonify({'error': 'Email already in the Newsletter'}), 404

    if email:
        new_email= Newsletter(
            email=email,
            creation_date=datetime.today().strftime("%Y-%m-%d %H:%M"),
            is_active_email=False,
            has_opt_out=False,
            nbr_email_opened=0,
            nbr_email_received=0
        )

        try:
            db.session.add(new_email)
            db.session.commit()
            return jsonify({'message': 'Email added successfully'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to add email', 'details': str(e)}), 500
        

@activity_blueprint.route('/user-my-activity-settings', methods=['GET'])
@jwt_required()
def get_user_my_activity():

    if request.method == 'GET':
        user_email = get_jwt_identity()['email']

        if user_email:

            email_news =  (
                            db.session.query(
                                cast(func.date_trunc('day', func.to_timestamp(ActivityLog.activity_timestamp, 'YYYY-MM-DD HH24:MI:SS')), Date).label('date'),
                                func.sum(case(((ActivityLog.activity_type == 'click_search_submit', 1)), else_=0)).label('estimateVolume'),
                                func.sum(case(((ActivityLog.activity_type == 'click_history_search', 1)), else_=0)).label('searchVolume')
                            )
                            .filter(
                                ActivityLog.user_email == user_email,
                                ActivityLog.activity_type.in_(["click_search_submit", "click_history_search"]),
                            )
                            .group_by(
                                cast(func.date_trunc('day', func.to_timestamp(ActivityLog.activity_timestamp, 'YYYY-MM-DD HH24:MI:SS')), Date)
                            )
                            .order_by(  
                                cast(func.date_trunc('day', func.to_timestamp(ActivityLog.activity_timestamp, 'YYYY-MM-DD HH24:MI:SS')), Date)
                            )
                            .all()
                        )
            
            result = [
                {
                    "date": str(record.date),
                    "estimateVolume": record.estimateVolume,
                    "searchVolume": record.searchVolume
                }
                for record in email_news
            ]

            return jsonify({"result": result}), 200