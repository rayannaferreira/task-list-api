from flask import Blueprint, abort, make_response, request
from app.models.goal import Goal
from app.db import db


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
