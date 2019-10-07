from flask import Blueprint

from app.app import app

index_bp = Blueprint('index', __name__)


@index_bp.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
