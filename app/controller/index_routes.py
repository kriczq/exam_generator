from flask import Blueprint

from app.app import app

index_routes = Blueprint('index', __name__)


@index_routes.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
