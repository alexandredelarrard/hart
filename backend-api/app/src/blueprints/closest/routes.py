from flask import request, jsonify
from sqlalchemy import desc
import numpy as np
import logging
import base64
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from celery.result import AsyncResult
from celery.utils import uuid
from datetime import datetime

from src.backend.tasks import process_request
from src.schemas.results import CloseResult
from src.schemas.payment import PaymentTrack
from src.extensions import db

from src.extensions import front_server
from . import closest_blueprint


@closest_blueprint.route("/process", methods=["POST"])
@cross_origin(origins=front_server)
@jwt_required()
def process():

    if request.method == "POST":

        user_id = request.form["user_id"]

        text = request.form.get("text", None)
        file = request.files.get("file", None)
        image = file.read() if file else None

        if not image and not text:
            return jsonify({"error": "Missing image and text"}), 400

        # save the task in db
        result_image = base64.b64encode(image).decode("utf-8") if image else None

        # Generate a unique task ID
        task_id = uuid()

        # Save the new result in the database
        # TODO: pydantic for llm_result & JSON type instead of str
        new_result = CloseResult(
            user_id=user_id,
            task_id=task_id,
            file=result_image,
            text=text,
            creation_date=datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            status="SENT",
            visible_item=True,
        )
        db.session.add(new_result)
        db.session.commit()

        # create new task after having a new element
        task = process_request.apply_async(args=[image, text], task_id=task_id)

        # update the volume of search with -1 with the last payment plan
        payment = (
            PaymentTrack.query.filter_by(user_id=user_id)
            .order_by(desc(PaymentTrack.plan_start_date))
            .first()
        )
        if payment:
            payment.remaining_closest_volume -= 1
            db.session.commit()
        else:
            logging.info(f"payment not found for ID {user_id}")

        return jsonify({"task_id": task.id}), 202


@closest_blueprint.route("/task_status", methods=["POST"])
@cross_origin(origins=front_server)
@jwt_required()
def task_status():

    if request.method == "POST":
        data = request.get_json()
        task_id = data.get("taskid")
        task = AsyncResult(task_id)

        if task.state == "PENDING":
            response = {"state": task.state, "status": "Pending..."}

        elif task.state == "SUCCESS":
            response = {
                "state": task.state,
                "result": task.result,
            }

            # save result into db
            try:
                result = CloseResult.query.filter_by(task_id=task_id).first_or_404()

                if result:
                    result.answer = task.result["answer"]
                    result.status = task.state
                    result.result_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    db.session.commit()

            except Exception as e:
                print(f"Error for saving result as {e}")

        else:
            response = {
                "state": task.state,
                "status": str(task.info),
            }

        return jsonify(response)
