from app import db
from sqlalchemy.orm import backref, validates


association_table = db.Table('association', db.Model.metadata,
    db.Column('question_id', db.Integer, db.ForeignKey('question.id')),
    db.Column('tag_name', db.Integer, db.ForeignKey('tag.name'))
)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(64), nullable=False)
    is_open = db.Column(db.Boolean, default=False)
    answers = db.relationship("Answer")
    tags = db.relationship(
        "Tag",
        secondary=association_table,
        back_populates="questions",
        single_parent=True,
        cascade="all, delete-orphan")
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'answers': [a.serialize for a in self.answers],
            'tags': [t.serialize for t in self.tags]
        }

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(64), nullable=False)
    correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'correct': self.correct
        }

class Tag(db.Model):
    name = db.Column(db.String(64), primary_key=True)
    questions = db.relationship(
        "Question",
        secondary=association_table,
        back_populates="tags")

    def __init__(self, name): 
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
      return hash(self.name)
    
    @property
    def serialize(self):
        return self.name