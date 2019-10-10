from flask import request, Blueprint
from marshmallow import ValidationError

from app.controller.utils.response_builder import build_response
from app.model.exam.exam_file_generator import generate_exam_groups_files
from app.model.exam.metadata_extractor import extract_exam_metadata

exam_generator_routes = Blueprint('exam', __name__, url_prefix='/exam')


@exam_generator_routes.route('/generate', methods=['POST'])
def generate_exam():
    json_data = request.get_json()

    try:
        closed_questions_number, number_of_groups, opened_questions_number, tags = extract_exam_metadata(json_data)
    except ValidationError as e:
        return {'error': e.messages}, 422

    try:
        groups_exam_files = generate_exam_groups_files(closed_questions_number, opened_questions_number, tags,
                                                       number_of_groups)
    except ValueError:
        return {'error': 'Nie znaleziono wystarczającej liczby pytań w bazie dla podanych argumentów'}, 422

    return build_response({'files': groups_exam_files}, status_code=200)
