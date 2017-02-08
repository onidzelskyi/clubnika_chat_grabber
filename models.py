# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser


# Read config
config = configparser.ConfigParser()
config.read('defaults.cfg')


# Flask app
app = Flask(__name__)
app.config.from_object(config.get('Models', 'app_config'))
db = SQLAlchemy(app)
db.create_all()

# Table('mytable', metadata,
#       Column('data', String(32)),
#       mysql_engine='InnoDB',
#       mysql_charset='utf8',
#       mysql_key_block_size="1024"
#      )

class Message(db.Model):
    __tablename__ = "messages"
    
    # id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP)
    date = db.Column(db.DATE)
    msg = db.Column(db.String(length=512))
    phone = db.Column(db.String(length=16))
    label = db.Column(db.String(length=16))

    # Primary key constraint
    __table_args__ = (db.PrimaryKeyConstraint('timestamp', 'msg', name='uix_1'),)

    def __init__(self, date, timestamp, msg, phone='', label=''):
        self.date = date
        self.timestamp = timestamp
        self.msg = msg
        self.phone = phone
        self.label = label
        #self.id = md5.md5(msg.encode('utf-8')).hexdigest()

    def __str__(self):
        return 'date: {item.date} timestamp: {item.timestamp} msg {item.msg}'.format(item=self)