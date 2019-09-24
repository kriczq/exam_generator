from app.app import app
from app.models import Question, Answer, Tag
from app import db
from flask import request, json, Response, Blueprint, jsonify, render_template, url_for
from sqlalchemy.sql import func
from xhtml2pdf import pisa 
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
    return 'Hello World!'

@app.route('/questions', methods=['GET'])
def all_questions():
    questions = Question.query.all()

    # return make_response(questions, 200)
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


    print(data)

    if data['is_open']:
      q = Question(text=data['text'], is_open=True, tags=data['tags'])
    else:
      q = Question(text=data['text'], answers=data['answers'], tags=data['tags'])
    
    db.session.add(q)
    db.session.commit()
    return make_response(q, 201)

    # answers = list(map(lambda x: Answer(text=x['text'], correct=x['correct']), req['answers']))
    # tags = []

    # for t in req['tags']:
    #     tag = Tag.query.get(t)
    #     if tag:
    #         tags.append(tag)
    #     else:
    #         tags.append(Tag(name=x))

    # q = Question(text=req['text'], answers=answers, tags=tags)
    # db.session.add(q)
    # db.session.commit()
    # return make_response(q, 201)

    db.session.add(data)
    db.session.commit()
    return '', 200

@app.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    question = Question.query.get(question_id)
    req = request.get_json()

    # for answer in req['answers']:
    #     result = (q.id = asnwer['id'] for a in question.answers).next()
    #     if result:
    #         result.text = answer['text']
    #         result.correct = answer['correct']
    #     else:
    #         question.answers.append(Answer(text=answer['text'], correct=answer['correct']))
    question.text = req['text']

    new_tags = []

    for tag_name in req['tags']:
        result = next((t for t in question.tags if t.name == tag_name), None)
        if result:
            new_tags.append(result)
        else:
            new_tags.append(Tag(name=tag_name))
    
    question.tags = new_tags

    # new_answers = list(map(lambda x: Answer(id=x.get('id', None) ,text=x['text'], correct=x['correct']), req['answers']))
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

def convertHtmlToPdf(sourceHtml, outputFilename):
    # open output file for writing (truncated binary)
    resultFile = open(outputFilename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
            sourceHtml,                # the HTML to convert
            dest=resultFile,
            encoding='utf-8')           # file handle to recieve result

    # close output file
    resultFile.close()                 # close output file

    # return True on success and False on errors
    return pisaStatus.err

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

    # 9 pytan 5 tagow
    # 1 1 2 2 3
    # 0 0 1 1 2

    tags = data['tags']

    if not tags:
      tags = Tag.query.all()

    # if closed_questions_number > 0:
    #   tags_open_count = list(map(lambda x: Question.query.filter(Question.tags.any(name=x.name), Question.is_open == True).count(), tags))
    
    
    # tags_closed_count = list(map(lambda x: Question.query.filter(Question.tags.any(name=x.name), Question.is_open == False).count(), tags))
    
    # try:
    #   tags_open_to_choose = get_tags(tags_open_count, opened_questions_number)
    #   tags_closed_to_choose = get_tags(tags_closed_count, closed_questions_number)
    # except ValueError as e:
    #   return {'error': 'there are not enough questions with given tags'}, 422

    # questions = []

    # if 
    # for (i, tag) in enumerate(tags):
    #     if tags_open_to_choose[i] > 0:
    #       questions += Question.query.filter(Question.tags.any(name=tag.name), Question.is_open == True).order_by(func.random()).limit(tags_open_to_choose[i]).all()
        
    #     if tags_closed_to_choose[i] > 0:
    #       questions += Question.query.filter(Question.tags.any(name=tag.name), Question.is_open == False).order_by(func.random()).limit(tags_closed_to_choose[i]).all()
    
    # print(questions)
          # HTML(render_template('pdf_template.html', questions=questions)).write_pdf('/tmp/weasyprint-website.pdf')
      
    random_uuid = uuid.uuid4().hex
    os.makedirs(os.path.join('app', 'static', random_uuid))
    files = []

    for i in range(1, groups_number + 1):
      random.shuffle(tags)

      try:
        questions = rand_questions(tags, closed_questions_number)
      except ValueError as e:
        return {'error': 'there are not enough questions with given tags'}, 422

      file_name = 'grupa_{}.pdf'.format(i)
      convertHtmlToPdf(render_template('pdf_template.html', questions=questions), os.path.join('app', 'static', random_uuid, file_name))
      files.append(url_for('static', filename=('{}/{}'.format(random_uuid, file_name))))

    return make_response({ 'files': files }, status_code=200)