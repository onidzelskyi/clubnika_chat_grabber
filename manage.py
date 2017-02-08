from manager import Manager

from models import db


manager = Manager()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def create_db():
    db.create_all()


if __name__ == '__main__':
    manager.main()