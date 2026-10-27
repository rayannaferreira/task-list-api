from flask import abort, make_response
from app.db import db


def validate_model(cls, model_id):
    is_task = cls.__name__ == "Task"
    model_name = cls.__name__.lower()
    error_key = "details" if is_task else "message"

    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        response = {error_key: f"{model_name} {model_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if model is None:
        message = "Task not found" if is_task else f"{model_name} {model_id} not found"
        abort(make_response({error_key: message}, 404))

    return model


def create_model(cls, model_data):
    if not isinstance(model_data, dict):
        abort(make_response({"details": "Invalid data"}, 400))

    try:
        model = cls.from_dict(model_data)
    except KeyError:
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(model)
    db.session.commit()

    return model
