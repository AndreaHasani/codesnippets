import json
import time
import re

from flask import current_app, Flask, render_template, request, session, jsonify, abort, Blueprint
from app.models import Answers, Questions, db
from app.functions import *
from . import celery_app
from lxml import html
from lxml.etree import HTMLParser
from app.functions import AlchemyEncoder
from stackapi import StackAPI
from urllib.parse import unquote
from app.celery_tasks import insertQuestion

whitespace_parser = HTMLParser(remove_blank_text=True)
# stackOverflowConnection = StackAPI('stackoverflow')
# stackOverflowConnection.page_size = 20
# stackOverflowConnection.max_pages = 1

bp = Blueprint('main', __name__, url_prefix='/', static_folder='static')


# def stackApiRun(question):
#     returnedAnswers = stackOverflowConnection.fetch(
#         'questions/{ids}/answers', ids=question, sort='votes', filter="withbody")

#     # answerID = [items['answer_id'] for items in returnedAnswers['items']][0:20]

#     # api_answers = stackOverflowConnection.fetch(
#     #     'answers/{ids}', ids=answerID, sort='votes', filter="withbody")

#     output_answers = []
#     for answer in returnedAnswers['items']:
#         output_answers.append({'accepted': answer['is_accepted'], 'votes': answer['score'],
#                                'author': answer['owner']['display_name'], 'source': "stackoverflow",
#                                'url': "https://stackoverflow.com/a/{}/{}".format(answer['answer_id'], answer['owner']['user_id']),
#                                'answer': parseCode(answer['body'])})
#     return output_answers

def stack_get_answers(question_id):
    returnedAnswers = stackOverflowConnection.fetch(
        'questions/{ids}/answers', ids=[int(question_id)], sort='votes', filter="withbody")

    # answerID = [items['answer_id'] for items in returnedAnswers['items']][0:20]

    # api_answers = stackOverflowConnection.fetch(
    #     'answers/{ids}', ids=answerID, sort='votes', filter="withbody")

    output_answers = []
    for answer in returnedAnswers['items']:
        try:
            answer['url'] = "https://stackoverflow.com/a/{}".format(answer['answer_id'])
        except:
            pass
        answer['source'] = "stackoverflow"
        answer['body'] = parseCode(answer['body'])
        output_answers.append(answer)
    return output_answers

def stack_get_questions(q, tags=None):
    """
    : Query stackexchange api for :q
    : q -> question string to query the api
    : tags -> question string to query the api
    """
    if tags:
        tags = list(map(lambda x: x.replace("[", "").replace("]", ""), tags))
        questionSearch = stackOverflowConnection.fetch(
            'search/excerpts', q=q, sort='relevance', accepted=True, tagged=",".join(tags), answers=1)
    questions = []
    for question in questionSearch['items']:
        questions.append({
            "question_id": question['question_id'],
            "title": question['title'],
            "tags": question['tags'],
            "votes": question['score'],
            "answers_num": question['answer_count'],
            "answered": question['is_answered'],
            "source": "stackoverflow",
            "url": "https://stackoverflow.com/a/{}".format(question['question_id']),
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
    q = re.sub("\[.+?]", '', search_var).strip()
    local_questions = db.session.query(Questions).limit(4).all()
    if local_questions:
        questions = json.loads(json.dumps(local_questions, cls=AlchemyEncoder))
        # accepted = [item for item in answers if item['accepted']]
        # notAccepted = [item for item in answers if not item['accepted']]
        return jsonify(sorted(questions, key=lambda x: -x['votes']))
    else:
        stack_questions = stack_get_questions(q, tags)
        return jsonify(stack_questions)


@bp.route("/<question_id>/<question_title>", methods=["GET"])
def getAnswers(question_id, question_title):
    # items = db.session.query(Answers).all()
    # for item in items:
    #     item.answer = parseCode(item.answer)
    # answers = json.loads(json.dumps(items, cls=AlchemyEncoder))
    # accepted = [item for item in answers if item['accepted']]
    # notAccepted = [item for item in answers if not item['accepted']]
    # answers = stackApiRun(search_var)
    answers = stack_get_answers(question_id)
    title = unquote(question_title)
    return render_template("index.html", answer_items=answers, title=title)

