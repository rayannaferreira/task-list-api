from datetime import datetime
import os

from flask import Blueprint, jsonify, request
import requests

from app.db import db
from app.models.task import Task
from app.routes.route_utilities import create_model, validate_model


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "title" not in data or "description" not in data:
        return jsonify({"details": "Invalid data"}), 400

    task = create_model(Task, data)

    return jsonify(task.to_dict()), 201


@tasks_bp.get("/tasks")
def get_tasks():
    sort = request.args.get("sort")
    query = db.select(Task)

    if sort == "asc":
        query = query.order_by(Task.title.asc())
    elif sort == "desc":
        query = query.order_by(Task.title.desc())

    tasks = db.session.scalars(query).all()
    tasks_list = [task.to_dict() for task in tasks]

    return jsonify(tasks_list), 200


@tasks_bp.get("/tasks/<task_id>")
def get_task(task_id):
    task = validate_model(Task, task_id)

    return jsonify(task.to_dict()), 200


@tasks_bp.put("/tasks/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "title" not in data or "description" not in data:
        return jsonify({"details": "Invalid data"}), 400

    task.title = data["title"]
    task.description = data["description"]

    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}


@tasks_bp.delete("/tasks/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}


@tasks_bp.patch("/tasks/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {os.environ.get('SLACK_API_KEY')}"},
        json={
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}",
        },
        timeout=10,
    )

    return "", 204, {"Content-Type": "application/json"}


@tasks_bp.patch("/tasks/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}
