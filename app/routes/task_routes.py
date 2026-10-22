from flask import Blueprint, request, jsonify
from app.models.task import Task
from app.db import db
from datetime import datetime
import requests
import os

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "title" not in data or "description" not in data:
        return jsonify({"details": "Invalid data"}), 400

    new_task = Task.from_dict(data)

    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201


@tasks_bp.route("/tasks", methods=["GET"])
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


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"details": "Task not found"}), 404

    return jsonify(task.to_dict()), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"details": "Task not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "title" not in data or "description" not in data:
        return jsonify({"details": "Invalid data"}), 400

    task.title = data["title"]
    task.description = data["description"]

    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"details": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return "", 204, {"Content-Type": "application/json"}


@tasks_bp.route("/tasks/<int:task_id>/mark_complete", methods=["PATCH"])
def mark_complete(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"details": "Task not found"}), 404

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

    return jsonify(task.to_dict()), 204


@tasks_bp.route("/tasks/<int:task_id>/mark_incomplete", methods=["PATCH"])
def mark_incomplete(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        return jsonify({"details": "Task not found"}), 404

    task.completed_at = None
    db.session.commit()

    return jsonify(task.to_dict()), 204
