from flask import request, jsonify
from typing import Dict, Any
import math
from sqlalchemy import and_, or_
import numpy as np
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required

from src.schemas.crawling_cleaning import AllItems
from src.schemas.results import CloseResult
from src.extensions import db
from src.constants.models import KnnFullResultInfos, EmbeddingsResults
from src.extensions import front_server
from . import infos_blueprint


def filter_non_null_values(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        k: v
        for k, v in data.items()
        if v is not None and not (isinstance(v, float) and math.isnan(v))
    }


def enrich_dict(
    answer: EmbeddingsResults, additional_info_dict: KnnFullResultInfos
) -> KnnFullResultInfos:

    new_list = []
    for element in additional_info_dict.answer:
        if element.id_item in answer.keys():
            updated_element = element.copy(
                update=filter_non_null_values(answer[element.id_item])
            )
            new_list.append(updated_element)
        else:
            new_list.append(element)
    return KnnFullResultInfos(answer=new_list)


def fetch_additional_infos(answer: EmbeddingsResults) -> KnnFullResultInfos:
    filtered_items = (
        db.session.query(AllItems)
        .filter(AllItems.id_item.in_(list(answer.keys())))
        .all()
    )
    return KnnFullResultInfos(answer=[item.to_dict_search() for item in filtered_items])


# =============================================================================
# additonal infos
# =============================================================================
@infos_blueprint.route("/ids_infos", methods=["POST"])
@cross_origin(origins=front_server)
@jwt_required()
def post_ids_infos():

    if request.method == "POST":
        data = request.get_json()
        answer = data.get("answer")

        if not answer:
            return jsonify({"error": "No answer provided"}), 400

        if isinstance(answer, dict):

            # try:

            # Fetch filtered items in batches
            additional_infos = fetch_additional_infos(answer)
            knn_full_output = enrich_dict(answer, additional_infos)

            # results
            denominator = np.sum(
                [
                    1 / (10 * float(x.distance) + 0.01) ** 2
                    for x in knn_full_output.answer
                    if isinstance(x.estimate_min, float)
                ]
            )
            min_estimate = (
                np.round(
                    np.sum(
                        [
                            x.estimate_min / (10 * float(x.distance) + 0.01) ** 2
                            for x in knn_full_output.answer
                            if isinstance(x.estimate_min, float)
                        ]
                    )
                    / denominator
                    / 10,
                    0,
                )
                * 10
            )
            max_estimate = (
                np.round(
                    np.sum(
                        [
                            x.estimate_max / (10 * float(x.distance) + 0.01) ** 2
                            for x in knn_full_output.answer
                            if isinstance(x.estimate_max, float)
                        ]
                    )
                    / denominator
                    / 10,
                    0,
                )
                * 10
            )
            final_result = (
                np.round(
                    np.sum(
                        [
                            x.final_result / (10 * float(x.distance) + 0.01) ** 2
                            for x in knn_full_output.answer
                            if isinstance(x.final_result, float)
                        ]
                    )
                    / denominator
                    / 10,
                    0,
                )
                * 10
            )

            return (
                jsonify(
                    {
                        "result": knn_full_output.dict(),
                        "min_estimate": min_estimate,
                        "max_estimate": max_estimate,
                        "final_result": final_result,
                    }
                ),
                200,
            )

        # except Exception as e:
        #     return jsonify({"error": str(e)}), 500

        else:
            return jsonify({"error": "ids does not have the expected format"}), 401


@infos_blueprint.route("/get-past-results", methods=["GET"])
@cross_origin(origins=front_server)
@jwt_required()
def get_past_results():

    if request.method == "GET":
        user_id = request.args.get("user_id")
        if user_id:
            results = CloseResult.query.filter(
                CloseResult.user_id == user_id,
                or_(CloseResult.status == "SUCCESS", CloseResult.status == "SENT"),
                CloseResult.visible_item == True,
            ).all()
            list_results = [item.to_dict() for item in results]
            return jsonify({"results": list_results}), 200
        else:
            return jsonify({"error": "missing user ID"}), 400

    else:
        return jsonify({"error": "method only GET"}), 500


@infos_blueprint.route("/delete-task/<task_id>", methods=["DELETE"])
@cross_origin(origins=front_server)
@jwt_required()
def delete_task(task_id):

    if request.method == "DELETE":
        task = CloseResult.query.filter_by(task_id=task_id).first_or_404()

        if task_id:
            task.visible_item = False
            db.session.commit()
            return jsonify({"message": "successful deletion"}), 200
        else:
            return jsonify({"error": "missing task ID"}), 400

    else:
        return jsonify({"error": "method only GET"}), 500
