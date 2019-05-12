from app.models import db, Questions, Answers
import time
from app import celery_app

@celery_app.task(name="print_and_wait")
def insertQuestion(question, answers):
    question_adding = Questions(**question)
    db.session.add(question_adding)
    db.session.commit()
    answers_adding = Answers(**answers)
    db.session.add(answers_adding)
    db.session.commit()
