from flask import request, jsonify
from typing import List
from flask_cors import  cross_origin
from src.schemas.user import AllItems, AllPerItem, CloseResult
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

# =============================================================================
# additonal infos
# =============================================================================
@infos_blueprint.route('/ids_infos', methods=['POST'])
@cross_origin(origins=front_server)
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
                output = [item.to_dict() for item in result_desc_id]
                deduplicated_output = deduplicate_dicts(output, "id_item")

                # Fetch filtered items in batches
                # A refaire avec table indexee sur ID_ITEM
                filtered_items = db.session.query(AllPerItem).filter(
                                    and_(
                                        AllPerItem.ID_ITEM.in_([x['id_item'] for x in output]),
                                        AllPerItem.ID_PICTURE.isnot(None)
                                    )
                                ).all()
                grouped_items= [item.to_dict() for item in filtered_items]
                dict_items = {grouped_items[i]["id_item"] : grouped_items[i]["id_picture"] for i in range(len(grouped_items))}

                # Add grouped pictures to the output
                deduplicated_output = add_distance(deduplicated_output, dict_items, column="pictures", id="id_item")

                # results 
                min_estimate = np.round(np.median([x["estimate_min"] for x in deduplicated_output if isinstance(x["estimate_min"], float)])/10, 0)*10
                max_estimate = np.round(np.median([x["estimate_max"] for x in deduplicated_output if isinstance(x["estimate_min"], float)])/10, 0)*10
                final_result = np.round(np.median([x["final_result"] for x in deduplicated_output if isinstance(x["estimate_min"], float)])/10, 0)*10

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
