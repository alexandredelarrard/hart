from flask import request, jsonify
from typing import List
from itertools import groupby
from operator import attrgetter
from flask_cors import  cross_origin
from src.schemas.user import AllItems, AllPerItem
from sqlalchemy import and_
from sqlalchemy.sql import func
from src.extensions import db

from . import infos_blueprint
from src.extensions import front_server

def add_distance(output, dict_distances):
    new_list = []
    for element in output:
        element["distance"] = dict_distances[element["id_unique"]]
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
    new_output = add_distance(output, dict_id_dist)
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

    # Aggregate ID_PICTURE per ID_ITEM
    filtered_items.sort(key=attrgetter('ID_ITEM'))
    grouped_items = {k: [item.ID_PICTURE for item in g] for k, g in groupby(filtered_items, key=attrgetter('ID_ITEM'))}
    
    return grouped_items

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
                output = reorder_output_on_dist(result_desc_id, ids, distances)
                deduplicated_output = deduplicate_dicts(output, "id_item")

                # Fetch filtered items in batches
                # A refaire avec table indexee sur ID_ITEM
                grouped_items = fetch_filtered_items(output)

                # Add grouped pictures to the output
                for item in output:
                    item['pictures'] = grouped_items.get(item['id_item'], [])

                return jsonify(deduplicated_output), 200
            # except Exception as e:
            #     return jsonify({"error": str(e)}), 500
            
        else:
            return jsonify({"error": 'ids does not have the expected format'}), 400
