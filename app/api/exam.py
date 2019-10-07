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
from app.helpers import make_response

exam_api = Blueprint('exam', __name__, url_prefix='/exam')


def get_tags(tags_count, to_pick):
    if sum(tags_count) < to_pick:
        raise ValueError

    pick_per_tag = to_pick // len(tags_count)
    tags_to_choose = [pick_per_tag if (x > pick_per_tag) else x for x in tags_count]

    i = 0

    while sum(tags_to_choose) < to_pick:
        if (tags_to_choose[i % len(tags_count)] < tags_count[i % len(tags_count)]):
            tags_to_choose[i % len(tags_count)] += 1

        i += 1

    return tags_to_choose


def rand_questions(tags, questions_number, rand_open=False):
    if questions_number == 0:
        return []

    tags_count = [Question.query.filter(Question.tags.any(name=x.name), Question.is_open == rand_open).count() for x in tags]
    tags_to_choose = get_tags(tags_count, questions_number)

    questions = []

    for (i, tag) in enumerate(tags):
        if tags_to_choose[i] > 0:
            questions += (Question.query
                          .filter(Question.tags.any(name=tag.name), Question.is_open == rand_open)
                          .order_by(func.random())
                          .limit(tags_to_choose[i])
                          .all())

    return questions


@exam_api.route('/generate', methods=['POST'])
def generate_exam():
    json_data = request.get_json()

    generate_exam_schema = GenerateExamSchema()

    try:
        data = generate_exam_schema.load(json_data)
    except ValidationError as e:
        return {'error': e.messages}, 422

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
            return {'error': 'Nie znaleziono wystarczającej liczby pytań w bazie dla podanych argumentów'}, 422

        file_name = 'grupa_{}.pdf'.format(i)
        convertHtmlToPdf(render_template('pdf_template.html', questions=questions, group=i), os.path.join(dir_path, file_name))
        files.append(url_for('static', filename=('exams/{}/{}'.format(random_uuid, file_name))))

    return make_response({'files': files}, status_code=200)
