from flask import request, Blueprint, jsonify
from marshmallow import ValidationError

from app.model.db.dao.QuestionDAO import question_schema, questions_list_schema, QuestionDAO
from app.controller.utils.response_builder import build_response

questions_routes = Blueprint('questions', __name__, url_prefix='/questions')


@questions_routes.route('/', methods=['GET'])
def all_questions():
    questions = QuestionDAO.get_all()

    return jsonify(questions_list_schema.dump(questions))


@questions_routes.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = QuestionDAO.get(question_id)

    return question_schema.dump(question), 200


@questions_routes.route('/', methods=['POST'])
def add_question():
    json_data = request.get_json()

    if not json_data:
        return {'error': 'No input data provided'}, 400

    try:
        question = question_schema.load(json_data)
    except ValidationError as e:
        return {'error': e.messages}, 422

    QuestionDAO.create(question)

    return build_response(question, 201)


@questions_routes.route('/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    json_data = request.get_json()

    if not json_data:
        return {'error': 'No input data provided'}, 400

    try:
        question = question_schema.load(json_data)
    except ValidationError as e:
        return {'error': e.messages}, 422

    updated_question = QuestionDAO.update(question_id, question)

    return build_response(updated_question, 204)


@questions_routes.route('/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    QuestionDAO.delete(question_id)

    return build_response(None, status_code=200)
