from app import ma
from app.models import Question, Answer, Tag
from marshmallow import fields, ValidationError, validates, validates_schema


class AnswerSchema(ma.ModelSchema):
    class Meta:
        model = Answer

    @validates('text')
    def validate_text(self, text):
        if len(text) == 0:
            raise ValidationError('Answer must not be empty')

        return text


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tag
        fields = ('name',)

    @validates('name')
    def validate_name(self, name):
        if len(name) == 0:
            raise ValidationError('Tag name must not be empty')

        return name


class QuestionSchema(ma.Schema):
    class Meta:
        model = Question
        fields = ('id', 'text', 'is_open', 'tags', 'answers')

    tags = ma.Nested(TagSchema, many=True)
    answers = ma.Nested(AnswerSchema, many=True)

    @validates('text')
    def validate_text(self, text):
        if len(text) == 0:
            raise ValidationError('Question must be not empty')

    @validates_schema()
    def validate_answers(self, data, **kwargs):
        print(data)
        if not data['is_open'] and len(data['answers']) < 2:
            raise ValidationError('Closed question must have at least two answers')


class GenerateExamSchema(ma.Schema):
    groups_number = fields.Int(required=True)
    opened_questions_number = fields.Int(required=True)
    closed_questions_number = fields.Int(required=True)
    tags = ma.Nested(TagSchema, many=True)
