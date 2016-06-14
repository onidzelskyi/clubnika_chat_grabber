# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import md5

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Message(db.Model):
    __tablename__ = "messages"
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Float)
    date = db.Column(db.String)
    msg = db.Column(db.String)
    phone = db.Column(db.String)
    label = db.Column(db.String)

    def __init__(self, date, timestamp, msg, phone='', label=''):
        self.date = date
        self.timestamp = timestamp
        self.msg = msg
        self.phone = phone
        self.label = label
        #self.id = md5.md5(msg.encode('utf-8')).hexdigest()