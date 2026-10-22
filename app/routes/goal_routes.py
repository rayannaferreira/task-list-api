from flask import Blueprint, abort, make_response, request
from app.models.goal import Goal
from app.db import db
from app.models.task import Task


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


def validate_goal(goal_id):
    try:
        goal_id = int(goal_id)
    except ValueError:
        abort(make_response({"message": f"goal {goal_id} invalid"}, 400))

    query = db.select(Goal).where(Goal.id == goal_id)
    goal = db.session.scalar(query)

    if not goal:
        abort(make_response({"message": f"goal {goal_id} not found"}, 404))

    return goal


@goals_bp.post("")
def create_goal():
    request_body = request.get_json(silent=True)

    if not isinstance(request_body, dict) or not request_body.get("title"):
        return {"details": "Invalid data"}, 400

    goal = Goal.from_dict(request_body)

    db.session.add(goal)
    db.session.commit()

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
    goal = validate_goal(goal_id)

    return goal.to_dict(), 200


@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_goal(goal_id)
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
    goal = validate_goal(goal_id)

    db.session.delete(goal)
    db.session.commit()

    response = make_response("", 204)
    response.mimetype = "application/json"
    return response


@goals_bp.post("/<goal_id>/tasks")
def assign_tasks_to_goal(goal_id):
    goal = validate_goal(goal_id)
    request_body = request.get_json()

    if not isinstance(request_body, dict) or not isinstance(
        request_body.get("task_ids"), list
    ):
        return {"details": "Invalid data"}, 400

    tasks = []

    for task_id in request_body["task_ids"]:
        if type(task_id) is not int:
            return {"details": "Task IDs must be integers"}, 400

        task = db.session.get(Task, task_id)

        if task is None:
            return {"details": f"Task {task_id} not found"}, 404

        tasks.append(task)

    goal.tasks = tasks

    db.session.commit()

    response = goal.to_dict()
    response.pop("title", None)
    response["task_ids"] = [task.id for task in goal.tasks]

    return response, 200


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = validate_goal(goal_id)

    goal_dict = goal.to_dict()

    goal_dict["tasks"] = []

    for task in goal.tasks:
        goal_dict["tasks"].append(task.to_dict())

    return goal_dict, 200
