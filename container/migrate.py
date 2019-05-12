from flask_script import Manager
from flask_migrate import MigrateCommand
from app import create_app
from app.models import Answers, Users, Questions


manager = Manager(create_app)
manager.add_command('db', MigrateCommand)



if __name__ == "__main__":
    manager.run()

