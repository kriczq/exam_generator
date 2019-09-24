from app.app import app
from app.models import Question, Answer, Tag
from app import db
from flask import request, json, Response, Blueprint, jsonify, render_template, url_for
from sqlalchemy.sql import func
from app.helpers import convertHtmlToPdf
from marshmallow import ValidationError
import uuid
import os

import random
from app.schemas import QuestionSchema, GenerateExamSchema

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


questions_schema = QuestionSchema(many=True)
question_schema = QuestionSchema()


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return app.send_static_file("index.html")


@app.route('/questions', methods=['GET'])
def all_questions():
    questions = Question.query.all()

    return jsonify(questions_schema.dump(questions))


@app.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get(question_id)

    return question_schema.dump(question), 200


@app.route('/questions', methods=['POST'])
def add_question():
    json_data = request.get_json()

    if not json_data:
        return {'error': 'No input data provided'}, 400
    
    try:
        data = question_schema.load(json_data)
    except ValidationError as e:
        return e.messages, 422
    except AssertionError:
        return {'error': str(e)}, 422

    if data['is_open']:
        q = Question(text=data['text'], is_open=True, tags=data['tags'])
    else:
        q = Question(text=data['text'], answers=data['answers'], tags=data['tags'])
    
    db.session.add(q)
    db.session.commit()
    return make_response(q, 201)


@app.route('/questions/<int:question_id>', methods=['PUT'])
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


@app.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()

    return make_response(None, status_code=200)


def get_tags(tags_count, to_pick):
    if sum(tags_count) < to_pick:
        raise ValueError

    pick_per_tag = to_pick // len(tags_count)
    tags_to_choose = list(map(lambda x: pick_per_tag if (x > pick_per_tag) else x, tags_count))

    i = 0

    while sum(tags_to_choose) < to_pick:
        if (tags_to_choose[i%len(tags_count)] < tags_count[i%len(tags_count)]):
            tags_to_choose[i%len(tags_count)] += 1
      
        i += 1
    
    return tags_to_choose


def rand_questions(tags, questions_number, rand_open=False):
    if questions_number == 0:
        return []
    
    tags_count = list(map(lambda x: Question.query.filter(Question.tags.any(name=x.name), Question.is_open == rand_open).count(), tags))
    tags_to_choose = get_tags(tags_count, questions_number)

    questions = []

    for (i, tag) in enumerate(tags):
        if tags_to_choose[i] > 0:
            questions += Question.query.filter(Question.tags.any(name=tag.name), Question.is_open == rand_open).order_by(func.random()).limit(tags_to_choose[i]).all()
    
    return questions


@app.route('/exam/generate', methods=['POST'])
def generate_exam():
    json_data = request.get_json()

    generate_exam_schema = GenerateExamSchema()

    try:
        data = generate_exam_schema.load(json_data)
    except ValidationError as e:
        return e.messages, 422

    groups_number = data['groups_number']
    closed_questions_number = data['closed_questions_number']
    opened_questions_number = data['opened_questions_number']

    tags = data['tags']

    if not tags:
        tags = Tag.query.all()

    random_uuid = uuid.uuid4().hex
    dir_path = os.path.join('app', 'static', 'exams', random_uuid)
    os.makedirs(dir_path)
    files = []

    for i in range(1, groups_number + 1):
        random.shuffle(tags)
        questions = []
        
        try:
            questions += rand_questions(tags, closed_questions_number)
            questions += rand_questions(tags, opened_questions_number, rand_open=True)
        except ValueError as e:
            return {'error': 'there are not enough questions with given tags'}, 422

        file_name = 'grupa_{}.pdf'.format(i)
        convertHtmlToPdf(render_template('pdf_template.html', questions=questions, group=i), os.path.join(dir_path, file_name))
        files.append(url_for('static', filename=('exams/{}/{}'.format(random_uuid, file_name))))

    return make_response({ 'files': files }, status_code=200)