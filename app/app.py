from app import create_app
from config import Config
from app.models import Question, Answer, Tag

app = create_app(Config)

from app.api.questions import questions_api
from app.api.exam import exam_api
from app.routes import index_bp

app.register_blueprint(index_bp)
app.register_blueprint(questions_api)
app.register_blueprint(exam_api)

if __name__ == '__main__':
    app.run()
