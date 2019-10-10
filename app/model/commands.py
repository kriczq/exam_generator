import click
import json

from app.app import app
from app import db
from app.model.db.models import Question, Tag
from app.model.db.schemas import QuestionSchema

questions_list_schema = QuestionSchema(many=True)


@app.cli.command('seed')
@click.argument('file', type=click.File())
def seed(file):
    if Question.query.count():
        return

    json_data = json.load(file)

    print('database is empty, add initial questions')
    data = questions_list_schema.load(json_data)
    for question in data:
        question.tags = [db.session.merge(Tag(tag.name)) for tag in question.tags]


    db.session.add_all(data)
    db.session.commit()
