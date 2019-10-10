from marshmallow import fields, ValidationError, validates, validates_schema

from app import ma
from app.model.db.models import Question, Answer, Tag


class AnswerSchema(ma.ModelSchema):
    class Meta:
        model = Answer

    @validates('text')
    def validate_text(self, text):
        if len(text) == 0:
            raise ValidationError('Odpowiedź nie może być pusta')

        if len(text) > 64:
            raise ValidationError('Maksymalna długość odpowiedzi wynosi 64 znaki')


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tag
        fields = ('name',)

    @validates('name')
    def validate_name(self, name):
        if len(name) == 0:
            raise ValidationError('Nazwa tagu nie może być pusta')

        if len(name) > 64:
            raise ValidationError('Nazwa tagu nie może przekraczać 64 znaków')


class QuestionSchema(ma.ModelSchema):
    class Meta:
        model = Question
        fields = ('id', 'text', 'is_open', 'tags', 'answers')

    tags = ma.Nested(TagSchema, many=True)
    answers = ma.Nested(AnswerSchema, many=True)

    @validates('text')
    def validate_text(self, text):
        if len(text) == 0:
            raise ValidationError('Pytanie nie może być puste')

        if len(text) > 64:
            raise ValidationError('Długość pytania nie może przekraczać 64 znaków')

    @validates('tags')
    def validate_tags(self, tags):
        if not tags:
            raise ValidationError('Pytanie musi zawierać co najmniej jeden tag')

    @validates_schema()
    def validate_answers(self, data, **kwargs):
        if not data.get('is_open', False):
            if len(data['answers']) < 2:
                raise ValidationError('Pytanie musi mieć co najmniej dwie odpowiedzi')

            if len([answer for answer in data['answers'] if answer.correct]) == 0:
                raise ValidationError('Pytanie musi mieć co najmniej jedną poprawną odpowiedź')


class GenerateExamSchema(ma.Schema):
    groups_number = fields.Int(required=True)
    opened_questions_number = fields.Int(required=True)
    closed_questions_number = fields.Int(required=True)
    tags = ma.Nested(TagSchema, many=True)
