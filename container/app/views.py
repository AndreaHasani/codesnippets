import json
import time
import re
from pprint import pprint

from flask import current_app, Flask, render_template, request, session, jsonify, abort, Blueprint
from app.models import Answers, Questions, db
from app.functions import *
from . import search

from lxml import html
from lxml.etree import HTMLParser
from app.functions import AlchemyEncoder
from stackapi import StackAPI
from urllib.parse import unquote
from app.celery_tasks import insertQuestion, insertAnswer

whitespace_parser = HTMLParser(remove_blank_text=True)
stackOverflowConnection = StackAPI('stackoverflow')
stackOverflowConnection.page_size = 20
stackOverflowConnection.max_pages = 1

bp = Blueprint('main', __name__, url_prefix='/', static_folder='static')


def stack_get_answers(question_id):
    """
    Api -> https://api.stackexchange.com/docs/types/answer
    """
    returnedAnswers = stackOverflowConnection.fetch(
        'questions/{ids}/answers', ids=[int(question_id)], sort='votes', filter="withbody")

    # answerID = [items['answer_id'] for items in returnedAnswers['items']][0:20]

    # api_answers = stackOverflowConnection.fetch(
    #     'answers/{ids}', ids=answerID, sort='votes', filter="withbody")

    output_answers = []
    for answer in returnedAnswers['items']:
        output_answers.append({
            "votes": answer.get("score"),
            "answer": parseCode(answer.get("body")),
            "accepted": answer.get("is_accepted"),
            "url": "https://stackoverflow.com/a/{}".format(
                answer['answer_id']),
            "author": answer.get("owner").get("display_name"),
            "source": "stackoverflow",
        })
    return output_answers


def stack_get_questions(q, tags=None):
    """
    : Query stackexchange api for :q
    : q -> question string to query the api
    : tags -> question string to query the api
    """
    questionSearch = stackOverflowConnection.fetch(
        'search/excerpts', q=q, sort='relevance', accepted=True, tagged=",".join(tags), answers=1)
    questions = []
    for question in questionSearch['items']:
        questions.append({
            "id": question.get('question_id') or None,
            "title": question.get("title"),
            "tags": ", ".join(question.get("tags")),
            "votes": question.get("score"),
            "answers_num": question.get("answer_count"),
            "answered": question.get("is_answered"),
            "source": "stackoverflow",
            "url": "https://stackoverflow.com/a/{}".format(question.get("question_id")),
        })

    return questions


def parseCode(code):
    source = html.fromstring(code, parser=whitespace_parser)
    code = source.cssselect("code")
    code = list(map(lambda x: x.text, code))
    return code


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/celery", methods=["POST", "GET"])
def running_celery():
    question = {
        "title": "Test db insert",
        "tags": "python",
        "votes": 50,
        "answers_num": 20,
        "answered": 1,
        "source": "codesnippets",
        "url": ""
    }
    answers = {
        "votes": 20,
        "answer": "Test answer for async",
        "accepted": 1,
        "source": "codesnippets",
        "url": ""
    }

    result = insertQuestion.apply_async(args=(question, answers))
    return "I sent a async request!"


@bp.route("/api/search", methods=["POST", "GET"])
def getQuestions():
    search_var = request.form.get("search_query", '')
    tags = re.findall("\[.+?]", search_var)
    if tags:
        tags = list(map(lambda x: x.replace("[", "").replace("]", ""), tags))

    q = re.sub("\[.+?]", '', search_var).strip()
    local_questions = Questions.query.search(
        q, tags_query=tags, or_=True, limit=4, fields=['title', 'tags']).all()
    if local_questions:
        questions = json.loads(json.dumps(local_questions, cls=AlchemyEncoder))
        return jsonify(sorted(questions, key=lambda x: -x['votes']))
    else:
        print("Using API")
        stack_questions = stack_get_questions(q, tags)
        insertQuestion.apply_async(args=(stack_questions[0],))
        return jsonify(stack_questions)


@bp.route("/<question_id>/<question_title>", methods=["GET"])
def getAnswers(question_id, question_title):
    local_answers = Answers.query.filter_by(question_id=question_id).all()
    title = unquote(question_title)
    if local_answers:
        for item in local_answers:
            code_answer = parseCode(item.answer)
        answers = json.loads(json.dumps(local_answers, cls=AlchemyEncoder))
        return render_template("index.html", answer_items=answers, title=title, cache_answer=code_answer)
    else:
        stack_answers = stack_get_answers(question_id)
        insertAnswer.apply_async(args=(stack_answers, question_id))
        insertAnswer(stack_answers, question_id)
        return render_template("index.html", answer_items=stack_answers, title=title)
