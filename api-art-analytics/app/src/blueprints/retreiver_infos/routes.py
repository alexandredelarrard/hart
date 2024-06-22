from flask import request, jsonify
from typing import List
from flask_cors import  cross_origin
from flask_jwt_extended import jwt_required
from src.schemas.items import AllItems, AllPerItem
from src.schemas.results import CloseResult
from sqlalchemy import and_
from src.extensions import db
import numpy as np

from . import infos_blueprint
from src.extensions import front_server

def add_distance(output, dict_distances, column, id):
    new_list = []
    for element in output:
        element[column] = dict_distances[element[id]]
        new_list.append(element)
    return new_list

def deduplicate_dicts(dict_list, unique_key):
    seen = {}
    for d in dict_list:
        if d[unique_key] not in seen:
            seen[d[unique_key]] = d
    return list(seen.values())

def reorder_output_on_dist(result, ids, distances):
    dict_id_dist = {ids[i] : distances[i] for i in range(len(ids))}
    output = [item.to_dict() for item in result]
    new_output = add_distance(output, dict_id_dist, column="distance", id="id_unique")
    sorted_output = sorted(new_output, key=lambda x: x["distance"])
    return sorted_output

def fetch_filtered_items(output):

    # get all pictures per id_unique 
    id_items = [x['id_item'] for x in output]
    filtered_items = db.session.query(AllPerItem).filter(
        and_(
            AllPerItem.ID_ITEM.in_(id_items),
            AllPerItem.ID_PICTURE.isnot(None)
        )
    ).all()

    return [item.to_dict() for item in filtered_items]

# =============================================================================
# additonal infos
# =============================================================================
@infos_blueprint.route('/ids_infos', methods=['POST'])
@cross_origin(origins=front_server)
@jwt_required()
def post_ids_infos():

    if request.method == 'POST':
        data = request.get_json()
        ids = data.get('ids')
        distances = data.get('distances')

        if not ids or not distances:
            return jsonify({"error": "No IDs provided"}), 400
        
        if isinstance(ids, List) and isinstance(distances, List):
            # try:
                # get description per id_unique
                result_desc_id =  AllItems.query.filter(AllItems.ID_UNIQUE.in_(ids)).all()
                output = reorder_output_on_dist(result_desc_id, ids, distances)
                deduplicated_output = deduplicate_dicts(output, "id_item")

                # Fetch filtered items in batches
                grouped_items = fetch_filtered_items(deduplicated_output)
                dict_items = {grouped_items[i]["id_item"] : grouped_items[i]["id_picture"] for i in range(len(grouped_items))}

                # Add grouped pictures to the output
                deduplicated_output = add_distance(deduplicated_output, dict_items, column="pictures", id="id_item")

                # results 
                denominator = np.sum([1/(10*float(x["distance"])+0.01)**2 for x in deduplicated_output if isinstance(x["estimate_min"], float)])
                min_estimate = np.round(np.sum([x["estimate_min"]/(10*float(x["distance"])+0.01)**2 for x in deduplicated_output if isinstance(x["estimate_min"], float)])/denominator/10, 0)*10
                max_estimate = np.round(np.sum([x["estimate_max"]/(10*float(x["distance"])+0.01)**2 for x in deduplicated_output if isinstance(x["estimate_max"], float)])/denominator/10, 0)*10
                final_result = np.round(np.sum([x["final_result"]/(10*float(x["distance"])+0.01)**2 for x in deduplicated_output if isinstance(x["final_result"], float)])/denominator/10, 0)*10

                return jsonify({"result": deduplicated_output, 
                                "min_estimate": min_estimate,
                                "max_estimate": max_estimate,
                                "final_result": final_result}), 200
            
            # except Exception as e:
            #     return jsonify({"error": str(e)}), 500
            
        else:
            return jsonify({"error": 'ids does not have the expected format'}), 400


@infos_blueprint.route('/get-past-results', methods=['GET'])
@cross_origin(origins=front_server)
@jwt_required()
def get_past_results():
    
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if user_id:
            results = CloseResult.query.filter_by(user_id=user_id, 
                                                  status="SUCCESS", 
                                                  visible_item=True).all()
            list_results= [item.to_dict() for item in results]
            return jsonify({"results": list_results}), 200
        else:
            return jsonify({"error": 'missing user ID'}), 400
    
    else:
        return jsonify({"error": 'method only GET'}), 500


@infos_blueprint.route('/delete-task/<task_id>', methods=['DELETE'])
@cross_origin(origins=front_server)
@jwt_required()
def delete_task(task_id):
    
    if request.method == 'DELETE':
        task = CloseResult.query.filter_by(task_id=task_id).first_or_404()

        if task_id:
            task.visible_item=False
            db.session.commit()
            return jsonify({"message": "successful deletion"}), 200
        else:
            return jsonify({"error": 'missing task ID'}), 400
    
    else:
        return jsonify({"error": 'method only GET'}), 500
