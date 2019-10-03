from app import create_app
from config import Config
from app.models import Question, Answer, Tag

app = create_app(Config)

from app.api.questions import questions
from app.api.exam import exam

# app.register_blueprint(index)
app.register_blueprint(questions)
app.register_blueprint(exam)

if __name__ == '__main__':
    app.run()
