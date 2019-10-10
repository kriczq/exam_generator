from app.model.db.models import Tag
from app.model.db.schemas import GenerateExamSchema


def extract_exam_metadata(json_data):
    data = GenerateExamSchema().load(json_data)

    number_of_groups = data['groups_number']
    closed_questions_number = data['closed_questions_number']
    opened_questions_number = data['opened_questions_number']
    tags = data['tags']

    if len(tags) == 0:
        tags = Tag.query.all()

    return closed_questions_number, number_of_groups, opened_questions_number, tags
