from flask import request, jsonify
from typing import List
from itertools import groupby
from operator import attrgetter
from flask_cors import  cross_origin
from src.schemas.user import AllItems
from sqlalchemy import and_
from sqlalchemy.sql import func
from src.extensions import db

from . import infos_blueprint
from src.extensions import front_server

BATCH_SIZE = 1000000

def add_distance(output, dict_distances):
    new_list = []
    for element in output:
        element["distance"] = dict_distances[element["id_unique"]]
        new_list.append(element)
    return new_list

def reorder_output_on_dist(result, ids, distances):
    dict_id_dist = {ids[i] : distances[i] for i in range(len(ids))}
    output = [item.to_dict() for item in result]
    output = add_distance(output, dict_id_dist)
    distances_output = [x["distance"] for x in output]
    return [x for _, x in sorted(zip(distances_output, output))]


def fetch_filtered_items(output):

    # get all pictures per id_unique 
    id_items = [x['id_item'] for x in output]

    filtered_items = []
    for i in range(0, len(id_items), BATCH_SIZE):
        batch_ids = id_items[i:i + BATCH_SIZE]
        batch_items = db.session.query(AllItems).filter(
            and_(
                AllItems.ID_ITEM.in_(batch_ids),
                AllItems.ID_PICTURE.isnot(None)
            )
        ).all()
        filtered_items.extend(batch_items)

    
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
            try:
                # get description per id_unique
                result_desc_id =  AllItems.query.filter(AllItems.ID_UNIQUE.in_(ids)).all()
                output = reorder_output_on_dist(result_desc_id, ids, distances)

                # Fetch filtered items in batches
                # A refaire avec table indexee sur ID_ITEM
                # grouped_items = fetch_filtered_items(output)

                # Add grouped pictures to the output
                # for item in output:
                #     item['pictures'] = grouped_items.get(item['id_item'], [])

                return jsonify(output), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
        else:
            return jsonify({"error": 'ids does not have the expected format'}), 400
