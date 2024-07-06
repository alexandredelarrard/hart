from flask import request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from sqlalchemy.sql import func
from src.schemas.items import AllPerItem

# from flask_limiter import Limiter

from . import search_db_blueprint
from src.extensions import front_server


# =============================================================================
# additonal infos
# =============================================================================
@search_db_blueprint.route("/search-items", methods=["GET"])
@cross_origin(origins=front_server)
@jwt_required()
# @limiter.limit("5 per minute")  # Allow 5 requests per minute per IP
def search_items():

    if request.method == "GET":
        query = request.args.get("q")

        if not query:
            return jsonify({"error": "No Query provided"}), 400

        if isinstance(query, str) and len(query) < 300:
            results = AllPerItem.query.filter(
                or_(
                    AllPerItem.ITEM_TITLE_DETAIL.ilike(f"%{query}%"),
                    AllPerItem.TOTAL_DESCRIPTION.ilike(f"%{query}%"),
                    # AllPerItem.HOUSE.ilike(f'%{query}%')
                )
            ).all()
            return jsonify({"result": [item.to_dict_search() for item in results]}), 200
        else:
            return (
                jsonify({"error": "query does not have the right type or length"}),
                400,
            )
