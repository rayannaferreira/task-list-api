from flask import Blueprint, make_response, request

from app.db import db
from app.models.goal import Goal
from app.models.task import Task
from app.routes.route_utilities import create_model, validate_model


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@goals_bp.post("")
def create_goal():
    request_body = request.get_json(silent=True)

    if not isinstance(request_body, dict) or not request_body.get("title"):
        return {"details": "Invalid data"}, 400

    goal = create_model(Goal, request_body)

    return goal.to_dict(), 201


@goals_bp.get("")
def get_all_goals():
    query = db.select(Goal).order_by(Goal.id)
    goals = db.session.scalars(query)

    goals_response = []

    for goal in goals:
        goals_response.append(goal.to_dict())

    return goals_response, 200


@goals_bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return goal.to_dict(), 200


@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json(silent=True)

    if not isinstance(request_body, dict) or not request_body.get("title"):
        return {"details": "Invalid data"}, 400

    goal.title = request_body["title"]

    db.session.commit()

    response = make_response("", 204)
    response.mimetype = "application/json"

    return response


@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    response = make_response("", 204)
    response.mimetype = "application/json"

    return response


@goals_bp.post("/<goal_id>/tasks")
def assign_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json(silent=True)

    if not isinstance(request_body, dict) or not isinstance(
        request_body.get("task_ids"), list
    ):
        return {"details": "Invalid data"}, 400

    tasks = []

    for task_id in request_body["task_ids"]:
        if type(task_id) is not int:
            return {"details": "Task IDs must be integers"}, 400

        task = validate_model(Task, task_id)
        tasks.append(task)

    goal.tasks = tasks

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks],
    }, 200


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    goal_dict = goal.to_dict()
    goal_dict["tasks"] = []

    for task in goal.tasks:
        goal_dict["tasks"].append(task.to_dict())

    return goal_dict, 200
