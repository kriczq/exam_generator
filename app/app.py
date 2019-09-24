from app import create_app
from config import Config
from app.models import Question, Answer, Tag

app = create_app(Config)

from app import routes

if __name__ == '__main__':
    app.run()