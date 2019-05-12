from flask import Flask, render_template, request
from app.config import Configuration
from flask_login import LoginManager
from app.functions import init_celery
from celery import Celery
from flask_migrate import Migrate

from multiprocessing import Process
import atexit
import os

global_process = ""

celery_app = Celery('app', config_source='app.celery_config')
migrate = Migrate()


def startCeleryWorker(application):
    celery_app.start(argv=['celery', 'worker', '-l', 'info'])


def stopProcess():
    global global_process
    global_process.terminate()

def create_app():
    """Creating flask app instance"""

    application = Flask(__name__)
    APP_DIR = os.path.dirname(os.path.realpath(__file__))
    application.config.from_object(Configuration)



    ## Init Celery
    init_celery(application, celery=celery_app)


    from app.models import db
    db.init_app(application)

    from app.views import bp
    application.register_blueprint(bp)

    ## Init Migrate
    migrate.init_app(application, db, compare_type=True)

    #Start celery worker on a new Proccess
    global global_process
    global_process = Process(target=startCeleryWorker, args=(application,))
    global_process.start()

    atexit.register(stopProcess)

    return application

