from app import db
from app.model.db.models import Question
from app.model.db.schemas import QuestionSchema

questions_list_schema = QuestionSchema(many=True)
question_schema = QuestionSchema()


class QuestionDAO:
    @classmethod
    def delete(cls, question_id):
        question_to_delete = Question.query.get(question_id)
        db.session.delete(question_to_delete)
        db.session.commit()

    @classmethod
    def create(cls, question):
        db.session.add(question)
        db.session.commit()
        return question

    @classmethod
    def get_all(cls):
        return Question.query.all()

    @classmethod
    def get(cls, question_id):
        return Question.query.get(question_id)

    @classmethod
    def update(cls, question_id, new_question):
        question = Question.query.get(question_id)
        question.text = new_question.text
        question.is_open = new_question.is_open
        question.tags = new_question.tags
        question.answers = new_question.answers

        db.session.commit()
        return question
