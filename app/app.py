from app import create_app
from config import Config

app = create_app(Config)

from app.controller.question_routes import questions_routes
from app.controller.generator_routes import exam_generator_routes
from app.controller.index_routes import index_routes
from app.model import commands

app.register_blueprint(index_routes)
app.register_blueprint(questions_routes)
app.register_blueprint(exam_generator_routes)


if __name__ == '__main__':
    app.run()
