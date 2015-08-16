#!/usr/bin/python
# -*- coding: utf-8 -*-

from scrapy import Selector
from requests import Request, Session
import urlparse
from selenium import webdriver
import os.path
import string
import codecs
import sqlite3
import re
import requests
import json


conn = sqlite3.connect('clubnika.db')

work_dir = os.path.dirname(os.path.abspath(__file__))
ts_file = "/timestamp.txt"
url = "http://clubnika.com.ua/home/"
# Empirical value
MAX_STEP_SIZE = 7


CHECK_PHONE = 1
CLASSIFY = 1


def createDB():
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS messages(timestamp TEXT, msg TEXT, phone TEXT, label TEXT)")


def saveEntry(batch):
    c = conn.cursor()
    c.executemany("INSERT INTO messages VALUES(?,?,?,?)",batch)
    conn.commit()


def checkPhone(batch):
    new_batch = []
    for entry in batch:
        # Omit digits in unicode format
        str = unicode(entry[1]).replace(u'\u0417', "3")
        
        # Leave only numbers in string
        str = re.sub("[^0-9]", " ", str)

        i = 0
        phone = ""
        phones = []
        for c in str:
            if c.isdigit():
                if i<MAX_STEP_SIZE:
                    i = 0
                    phone = phone + c
                elif len(phone):
                    phones.append(phone)
                    phone = c
                    i = 0
            elif len(phone):
                i = i+1

            if len(phone):
                phones.append(phone)
        lst = list(entry)
        a = [phone for phone in phones if len(phone)>8]
        lst[2] = a[0] if len(a) else ""
        new_batch.append(tuple(lst))
    return new_batch


def classify(batch):
    text_list = [x[1] for x in batch]
    data = {
        'text_list': text_list
    }
    response = requests.post(
                             "https://api.monkeylearn.com/v2/classifiers/cl_VL7oNpx2/classify/?sandbox=1",
                             data=json.dumps(data),
                             headers={'Authorization': 'Token 423b24aece62d16fc58e62de1490eeb06db2d80f',
                             'Content-Type': 'application/json'})
    labels = json.loads(response.text)["result"]
    new_batch = []
    for i,x in enumerate(batch):
        new_batch.append((batch[i][0], batch[i][1], batch[i][2], labels[i][0]["label"]))
    return new_batch


def fetchMsg():
    # Timestamp
    old_checkpoint = codecs.open(work_dir+ts_file, encoding="utf-8").read() if os.path.exists(work_dir+ts_file) else ''
    new_checkpoint = ''

    s = Session()

    header = {}
    post_data = {"login": "+380679695627", "password":"8027541", "signin":"Войти"}


    req = Request('POST', url,data = post_data, headers=header)

    prepped = req.prepare()

    prepped.headers["Referer"] = "http://clubnika.com.ua/home/"
    prepped.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    prepped.headers["Origin"] = "http://clubnika.com.ua"
    prepped.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"

    resp = s.send(prepped)
    browser = webdriver.Chrome()
    i = 1
    s1 = Session()
    completed = False
    batch = []
    while(1):
        url_tv_chat = "http://clubnika.com.ua/tv-chat/?action=view&room=1&page=" + str(i)
        req1 = Request('GET', url_tv_chat, cookies=resp.cookies, headers=header)
        prepped1 = req1.prepare()

        prepped1.headers["Referer"] = "http://clubnika.com.ua/guest/"
        prepped1.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        prepped1.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
        resp1 = s1.send(prepped1)

        open("/tmp/clubnika.html", "wb").write(resp1.content)
        browser.get("file:///tmp/clubnika.html")
        sel = Selector(text = browser.page_source)
        blocks = sel.xpath("//div[@class='p10']").extract()
        for block in blocks:
            sel1 = Selector(text = block)
            name = sel1.xpath('//div[@class="p10"]/b/text()').extract()
            if len(name)==0 or name[0] !=  u'\u041c\u043e\u0434\u0435\u0440':
                msg_body = sel1.xpath("//span[@class='c1']/text()").extract()
                if len(msg_body):
                    cur_ts = sel1.xpath("//small/text()").extract()[0]
                    msg_body = msg_body[0].replace('\n', ' ').replace('\r', '').replace(',', ' ')
                    check_point = cur_ts + "," + msg_body
                    batch.append((cur_ts, msg_body, '', '',))
                    if new_checkpoint=="":
                        new_checkpoint = check_point
                        if old_checkpoint=="":
                            open(work_dir+ts_file, "w").write(new_checkpoint.encode("utf8"))
                    if old_checkpoint.strip('\n') == check_point.strip('\n'):
                        open(work_dir+ts_file, "w").write(new_checkpoint.encode("utf8"))
                        completed = True
                        #os._exit(0)
        if CHECK_PHONE:
            batch = checkPhone(batch)
        if CLASSIFY:
            batch = classify(batch)
        saveEntry(batch)
        i = i+1


if __name__ == "__main__":
    createDB()
    fetchMsg()