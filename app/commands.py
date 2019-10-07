import click
import json
from flask.cli import with_appcontext

from app import db
from app.app import app
from app.models import Question
from app.schemas import QuestionSchema

questions_list_schema = QuestionSchema(many=True)


@app.cli.command('seed')
@click.argument('file', type=click.File())
def seed(file):
    if Question.query.count():
        return

    data = questions_list_schema.load(json.load(file))
    # db.session.add_all(data)
    # db.session.commit()
