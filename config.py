class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Pass1234@localhost/chat'
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://test:zhH-WAZ-WhY-d2V@chat-msg.cnoosqac3hj3.us-west-2.rds.amazonaws.com/chat'
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
