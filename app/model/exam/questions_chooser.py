import random
import itertools
from collections import Counter

from sqlalchemy.sql import func

from app.model.db.models import Question

MAX_ANSWERS_PER_QUESTION = 4


def choose_random_questions(tags, number_of_open_questions, number_of_closed_questions):
    open_questions = __extract_random_open_questions(tags, number_of_open_questions)
    closed_questions = __extract_random_closed_questions(tags, number_of_closed_questions)

    return closed_questions + open_questions


def __extract_random_open_questions(tags, questions_number):
    return __extract_random_questions(tags, questions_number, True)


def __extract_random_closed_questions(tags, questions_number):
    questions = __extract_random_questions(tags, questions_number, False)

    for question in questions:
        random.shuffle(question.answers)
        question.answers = question.answers[:MAX_ANSWERS_PER_QUESTION]

        if all(not answer.correct for answer in question.answers):
            question.answers[-1].text = 'Żadna z powyższych odpowiedzi'

    return questions


def __extract_random_questions(tags, questions_number, are_questions_open):
    if questions_number == 0:
        return []

    tags_count = Counter({
        (tag.name): (Question.query
                     .filter(Question.tags.any(name=tag.name), Question.is_open == are_questions_open)
                     .count())
        for tag in tags})

    questions_per_tag = __get_tags(tags_count, questions_number)

    # itertools used for flatten
    questions = list(itertools.chain.from_iterable(
        [(Question.query
          .filter(Question.tags.any(name=name), Question.is_open == are_questions_open)
          .order_by(func.random())
          .limit(count)
          .all()) for name, count in questions_per_tag.items() if count > 0]))

    return [PrintableQuestion(question) for question in questions]


def __get_tags(tags_counts, to_pick):
    if sum(tags_counts.values()) < to_pick:
        raise ValueError

    pick_per_tag = to_pick // len(tags_counts.keys())

    tags_to_choose = Counter({
        tag_name: pick_per_tag if (tag_count > pick_per_tag) else tag_count
        for tag_name, tag_count in tags_counts.items()})

    keys = tags_to_choose.keys()
    i = 0

    while sum(tags_to_choose.values()) < to_pick:
        key = keys[i % len(tags_counts)]

        if tags_to_choose[key] < tags_counts[key]:
            tags_to_choose[key] += 1

        i += 1

    return tags_to_choose


class PrintableQuestion:
    def __init__(self, question):
        self.text = question.text
        self.is_open = question.is_open
        self.answers = [PrintableAnswer(answer) for answer in question.answers]


class PrintableAnswer:
    def __init__(self, answer):
        self.text = answer.text
        self.correct = answer.correct
