#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import re
import datetime

from utils import *

report_file = 'report.txt'
db_file_name = 'test.db'
train_file_name = 'train.csv'

# probabilistic learning method
data = readCSV(train_file_name)
nb = NaiveBayes()
nb.trainModel(data)


# Read all text from db
conn = sqlite3.connect(db_file_name)
cur = conn.cursor()
start_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime("%s")
end_date = datetime.datetime.now().date().strftime("%s")
rows = cur.execute("select msg,date from messages  where timestamp  between ? and ?", (start_date, end_date)).fetchall()
data = [entry[0] for entry in rows]
date = [entry[1] for entry in rows]
response = nb.classify(data)
with open(report_file, 'wb') as fout:
  for i,entry in enumerate(response):
    if entry[1]=="1": fout.write("{} {}".format(date[i], entry[0].encode('utf-8')))
    print("{} {}\n".format(date[i], entry[0].encode('utf-8')))
