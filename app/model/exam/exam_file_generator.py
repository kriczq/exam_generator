import os
import random
import uuid

from flask import render_template, url_for

from app.model.exam.converters.html_to_pdf_converter import save_html_to_pdf
from app.model.exam.questions_chooser import choose_random_questions

EXAMS_BASE_DIR = os.path.join('app', 'static', 'exams')


def generate_exam_groups_files(number_of_closed_questions, number_of_open_questions, tags, number_of_groups):
    exam_uuid = uuid.uuid4().hex
    dir_path = __exam_files_dir(exam_uuid)

    return [__generate_exam_group_file(number_of_closed_questions,
                                       number_of_open_questions,
                                       tags,
                                       group_number,
                                       dir_path,
                                       exam_uuid) for group_number in range(1, number_of_groups + 1)]


def __generate_exam_group_file(number_of_closed_questions, number_of_open_questions, tags, group_number, dir_path, exam_uuid):
    file_name = __generate_exam_file(number_of_closed_questions, number_of_open_questions, tags, group_number, dir_path)
    return __build_exam_url(file_name, exam_uuid)


def __exam_files_dir(random_uuid):
    dir_path = os.path.join(EXAMS_BASE_DIR, random_uuid)
    os.makedirs(dir_path)
    return dir_path


def __generate_exam_file(number_of_closed_questions, number_of_open_questions, tags, group_number, dir_path):
    random.shuffle(tags)

    single_group_questions = choose_random_questions(tags, number_of_open_questions, number_of_closed_questions)
    new_exam_file_name = f'grupa_{group_number}.pdf'

    exam_html = render_template(
        'pdf_template.html',
        questions=single_group_questions,
        group=group_number,
        font_path=__get_font_path())
    save_html_to_pdf(exam_html, os.path.join(dir_path, new_exam_file_name))

    return new_exam_file_name


def __get_font_path():
    return ('..' if os.name == 'nt' else '.') + '/pdf_font/DejaVuSans.ttf'


def __build_exam_url(file_name, random_uuid):
    return url_for('static', filename=('exams/{}/{}'.format(random_uuid, file_name)))
