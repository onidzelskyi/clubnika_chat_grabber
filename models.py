# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser
import hashlib


# Read config
config = configparser.ConfigParser()
config.read('defaults.cfg')


# Flask app
app = Flask(__name__)
app.config.from_object(config.get('Models', 'app_config'))
db = SQLAlchemy(app)
db.create_all()

# meta = MetaData()
# messages = Table('messages', meta,
#                  Column('date', DateTime),
#                  Column('msg', String(512)),
#                  Column('phone', String(16)),
#                  Column('label', String(16)),
#                  PrimaryKeyConstraint(['invoice_id', 'ref_num'], ['invoice.invoice_id', 'invoice.ref_num'])
#                  )


class Message(db.Model):
    __tablename__ = "messages"
    
    # id = db.Column(db.Integer, primary_key=True)
    # timestamp = db.Column(db.TIMESTAMP)
    date = db.Column(db.DATETIME)
    msg = db.Column(db.String(length=1024))
    msg_checksum = db.Column(db.String(length=128))
    phone = db.Column(db.String(length=16))
    label = db.Column(db.String(length=16))

    # Primary key constraint
    __table_args__ = (db.PrimaryKeyConstraint('date', 'msg_checksum', name='uix_1'),
                      {'mysql_engine': 'InnoDB',
                       'mysql_charset': 'utf8'},
                      )

    def __init__(self, date, timestamp, msg, phone='', label=''):
        self.date = date
        # self.timestamp = timestamp
        self.msg = msg
        m = hashlib.sha256()
        m.update(msg.encode('utf-8'))
        self.msg_checksum = m.hexdigest()
        self.phone = phone
        self.label = label
        #self.id = md5.md5(msg.encode('utf-8')).hexdigest()

    def __str__(self):
        return 'date: {item.date} msg {item.msg}, hash: {item.msg_checksum}'.format(item=self)