from app.models import db, Questions, Answers
import time
from app import celery_app


@celery_app.task(name="db_insert_question")
def insertQuestion(question):
    question_adding = Questions(**question)
    db.session.add(question_adding)
    db.session.commit()
    # answers_adding = Answers(**answers, question_id=question_adding)
    # db.session.add(answers_adding)
    # db.session.commit()


# @celery_app.task(name="db_insert_answers")
def insertAnswer(answers, question_id):
    db_add_objects = []
    for answer in answers:
        answer["answer"] = "".join(
            list(map(lambda x: "<code>" + x + "</code>", answer['answer'])))
        db_add_objects.append(Answers(**answer, question_id=question_id))
    for adding_obj in db_add_objects:
        db.session.add(adding_obj)
    db.session.commit()
