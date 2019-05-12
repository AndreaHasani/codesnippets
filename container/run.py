from app import create_app
from celery.bin import worker

application = create_app()

if __name__ == '__main__':
    application.run()
    celery_options = {
        'broker': application.config['CELERY_BROKER_URL'],
        'loglevel': 'INFO',
        'traceback': True,
    }

