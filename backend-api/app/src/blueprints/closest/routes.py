from flask import request, jsonify
from . import closest_blueprint
from celery.result import AsyncResult
from datetime import datetime
from src.backend.tasks import process_request
from src.schemas.results import CloseResult
from src.extensions import db
import numpy as np


@closest_blueprint.route('/process', methods=['POST'])
def process():
    
    if request.method == 'POST':

        text = None
        if 'file' not in request.files:
            return jsonify({"error": "Missing picture"}), 400

        user_id = request.form['user_id']
        file = request.files['file']

        if 'text' in request.form:
            text = request.form['text']

        # Read the file content
        image = file.read()

        if not image and not text:
            return jsonify({"error": "Missing image and text"}), 400
 
        task = process_request.apply_async(args=[image, text])

        # save the task in db
        new_result = CloseResult(
            user_id=user_id,
            task_id=task.id,
            file=image,
            text=text,
            closest_ids="",
            closest_distances="",
            creation_date=datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            status="SENT",
            result_date=None,
            visible_item=True
            )
        db.session.add(new_result)
        db.session.commit()

        return jsonify({"task_id": task.id}), 202


@closest_blueprint.route('/task_status', methods=['POST'])
def task_status():

    if request.method == 'POST':
        data = request.get_json()
        task_id = data.get('taskid')
        task = AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Pending...'
            }

        elif task.state == 'SUCCESS':
            results = {"ids": task.result["image"]['ids'][0],
                       "distances": [np.round(x, 3) for x in task.result["image"]['distances'][0]]}
            
            response = {
                'state': task.state,
                'result': results,
            }

            # save result into db 
            try:
                result = CloseResult.query.filter_by(task_id=task_id).first_or_404()
        
                # Update the user as confirmed
                result.closest_ids = ",".join(results["ids"])
                result.closest_distances = ",".join([str(x) for x in results["distances"]])
                result.status = task.state
                result.result_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                db.session.commit()

            except Exception as e:
                print(f"Error for saving result as {e}")

        else:
            response = {
                'state': task.state,
                'status': str(task.info),
            }

        return jsonify(response), 200
