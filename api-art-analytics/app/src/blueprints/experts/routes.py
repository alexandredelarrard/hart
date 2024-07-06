from flask import request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from math import radians, cos, sin, asin, sqrt, acos
from . import experts_blueprint
from src.schemas.experts import Experts
from src.extensions import db
from src.extensions import front_server


@experts_blueprint.route("/get-experts-close", methods=["POST"])
@cross_origin(origins=front_server)
@jwt_required()
def get_close_expert():
    if request.method == "POST":
        data = request.get_json()
        user_longitude = data.get("longitude")
        user_latitude = data.get("latitude")

        print(user_longitude, user_latitude)

        try:
            user_longitude = float(user_longitude)
            user_latitude = float(user_latitude)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid coordinates"}), 400

        # Radius of Earth in kilometers. Use 6371 for km.
        radius = 6371

        # Haversine formula to calculate the great-circle distance
        # haversine = (acos(sin(radians(user_latitude)) * sin(radians(Experts.expert_latitude)) +
        #                         cos(radians(user_latitude)) * cos(radians(Experts.expert_latitude)) *
        #                         cos(radians(Experts.expert_longitude) - radians(user_longitude))) * radius)

        experts = db.session.query(Experts).all()  # .filter(haversine <= 150)
        experts_list = [expert.to_dict() for expert in experts]

        return jsonify({"result": experts_list}), 200
