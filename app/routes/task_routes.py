from datetime import datetime
import os
from flask import Blueprint, request, Response
import requests
from app.db import db
from app.models.task import Task
from app.routes.route_utilities import (
    create_model,
    validate_model,
    get_models_with_sort_response,
    call_slack_api
)


bp = Blueprint("tasks", __name__)


@bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True)
    task = create_model(Task, data)

    return task.to_dict(), 201


@bp.get("/tasks")
def get_tasks():
    return get_models_with_sort_response(Task, request.args), 200


@bp.get("/tasks/<task_id>")
def get_task(task_id):
    task = validate_model(Task, task_id)

    return task.to_dict(), 200


@bp.put("/tasks/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "title" not in data or "description" not in data:
        return {"details": "Invalid data"}, 400

    task.title = data["title"]
    task.description = data["description"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.delete("/tasks/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.patch("/tasks/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    call_slack_api(task)

    return Response(status=204, mimetype="application/json")

@bp.patch("/tasks/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")
