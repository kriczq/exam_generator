from app.models import Question, Answer, Tag
from app import db
from flask import request, json, Response, Blueprint, jsonify, render_template, url_for
from sqlalchemy.sql import func
from marshmallow import ValidationError
from app.schemas import QuestionSchema, GenerateExamSchema

from marshmallow import Schema, fields

questions_api = Blueprint('questions', __name__, url_prefix='/questions')


def serialize(obj):
    return obj.serialize


def make_response(res, status_code):
    if (res is not None):
        return Response(
            mimetype="application/json",
            response=json.dumps(res, default=serialize),
            status=status_code
        )
    else:
        return Response(
            status=status_code
        )


questions_list_schema = QuestionSchema(many=True)
question_schema = QuestionSchema()


@questions_api.route('/', methods=['GET'])
def all_questions():
    questions = Question.query.all()

    return jsonify(questions_list_schema.dump(questions))


@questions_api.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get(question_id)

    return question_schema.dump(question), 200


@questions_api.route('/', methods=['POST'])
def add_question():
    json_data = request.get_json()

    if not json_data:
        return {'error': 'No input data provided'}, 400

    try:
        data = question_schema.load(json_data)
    except ValidationError as e:
        return {'error': e.messages}, 422

    if data['is_open']:
        q = Question(text=data['text'], is_open=True, tags=data['tags'])
    else:
        q = Question(text=data['text'],
                     answers=data['answers'],
                     tags=data['tags'])
    db.session.add(q)
    db.session.commit()
    return make_response(q, 201)


@questions_api.route('/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    question = Question.query.get(question_id)
    req = request.get_json()

    question.text = req['text']
    new_tags = []

    for tag in req['tags']:
        tag_name = tag['name']
        result = next((t for t in question.tags if t.name == tag_name), None)

        if result:
            new_tags.append(result)
        else:
            new_tags.append(Tag(name=tag_name))

    question.tags = new_tags
    new_answers = []

    for a in req['answers']:
        a_obj = Answer(id=a.get('id', None), text=a['text'], correct=a['correct'])

        if (a_obj.id):
            a_obj = db.session.merge(a_obj)

        new_answers.append(a_obj)

    question.answers = new_answers

    db.session.commit()
    return make_response(question, 204)


@questions_api.route('/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()

    return make_response(None, status_code=200)
