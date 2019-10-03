from app.app import app
from app.models import Question, Answer, Tag
from app import db
from flask import request, json, Response, Blueprint, jsonify, render_template, url_for
from sqlalchemy.sql import func
from app.helpers import convertHtmlToPdf
from marshmallow import ValidationError
import uuid
import os

import random
from app.schemas import QuestionSchema, GenerateExamSchema


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')
