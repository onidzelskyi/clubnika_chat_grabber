#!/usr/bin/python
# -*- coding: utf-8 -*-

from scrapy import Selector
from requests import Request, Session
from selenium import webdriver
import os.path
import codecs
import re
import requests
import json
from pyvirtualdisplay import Display
import argparse  # Arguments parser
import time  # sleep
from sqlalchemy.exc import IntegrityError

from models import db, Message, config


class Grab(object):
    """Grab interface."""
    def __init__(self):
        self.work_dir = os.path.dirname(os.path.abspath(__file__))
        self.timestamp_file = config.getint('Grab', 'timestamp_file')
        self.deep_file = config.getint('Grab', 'deep_file')
        self.url = config.getint('Grab', 'url')
        self.deep = config.getint('Grab', 'deep')
        self.old_checkpoint = config.getint('Grab', 'old_checkpoint')
        self.new_checkpoint = config.getint('Grab', 'new_checkpoint')
        self.timeout = config.getint('Grab', 'timeout')
        self.check_phone = config.getint('Grab', 'check_phone')
        self.classify = config.getint('Grab', 'classify')
        self.max_step_size = config.getint('Grab', 'max_step_size')

    def load(self):
        self.parseArgs()
        self.create_db()
        self.loadOldCheckPoint()
        self.loadDeep()
        # Add current path to PATH environment variable for chrome driver
        os.environ["PATH"] += os.pathsep + self.work_dir

    def run(self):
        self.fetch_msg()

    def create_db(self):
        db.create_all()

    def fetch_msg(self):
        # Create session
        s = Session()

        # Fill up headers
        header = {}
        post_data = {"login": "+380679695627", "password": "8027541", "signin": "Войти"}
        req = Request('POST', self.url, data=post_data, headers=header)
        prepped = req.prepare()
        prepped.headers["Referer"] = "http://clubnika.com.ua/home/"
        prepped.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        prepped.headers["Origin"] = "http://clubnika.com.ua"
        prepped.headers[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"

        # Make request
        resp = s.send(prepped)

        # Run without GUI
        display = Display(visible=0, size=(800, 800))
        display.start()
        browser = webdriver.Chrome()

        s1 = Session()
        completed = False
        while (not completed):
            time.sleep(self.timeout)
            batch = []
            url_tv_chat = "http://clubnika.com.ua/tv-chat/?action=view&room=1&page=" + str(self.deep)
            req1 = Request('GET', url_tv_chat, cookies=resp.cookies, headers=header)
            prepped1 = req1.prepare()

            prepped1.headers["Referer"] = "http://clubnika.com.ua/guest/"
            prepped1.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            prepped1.headers[
                "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12"
            resp1 = s1.send(prepped1)

            # Save received page for rendering
            with open("/tmp/clubnika.html", "wb") as fp:
                fp.write(resp1.content)

            browser.get("file:///tmp/clubnika.html")
            sel = Selector(text=browser.page_source)
            blocks = sel.xpath("//div[@class='p10']").extract()
            for block in blocks:
                sel1 = Selector(text=block)
                name = sel1.xpath('//div[@class="p10"]/b/text()').extract()
                if len(name) == 0 or name[0] != u'\u041c\u043e\u0434\u0435\u0440':
                    msg_body = sel1.xpath("//span[@class='c1']/text()").extract_first()
                    if msg_body and len(sel1.xpath("//small/text()").extract()):
                        date_text = sel1.xpath("//small/text()").extract_first()
                        cur_ts = time.strptime(date_text, "%d.%m.%y %H:%M")
                        msg_body = msg_body.replace('\n', ' ').replace('\r', '').replace(',', ' ')
                        check_point = '{},{}'.format(date_text, msg_body)
                        timestamp = time.mktime(cur_ts)
                        message = Message(cur_ts, timestamp, msg_body)
                        db.session.add(message)
                        # batch.append((timestamp, cur_ts, msg_body, '', '',))
                        # At the first touch save new checkpoint
                        if self.new_checkpoint == '':
                            self.new_checkpoint = check_point.strip("\n")

                        if self.old_checkpoint == '' or self.outdated():
                            with open(self.work_dir + self.timestamp_file, "wb") as fp:
                                fp.write(self.new_checkpoint.encode("utf8"))

                        if self.old_checkpoint.strip('\n') == check_point.strip('\n'):
                            completed = True
                            break

                        if self.old_checkpoint == '':
                            self.old_checkpoint = self.new_checkpoint

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

            if self.check_phone:
                batch = self.checkPhone(batch)
            if self.classify:
                batch = self.classify(batch)
            self.saveEntry(batch)

            # next crawling page
            self.deep += 1

        # Save current deep
        if self.args.dig: self.saveDeep()

    # load last available checkpoint
    def loadOldCheckPoint(self):
        # Timestamp
        # If the program run in update mode
        # and file with the last timestamp exists
        # then load old checkpoint
        self.old_checkpoint = ''
        if os.path.exists(self.work_dir + self.timestamp_file):
            self.old_checkpoint = codecs.open(self.work_dir + self.timestamp_file, encoding="utf-8").read()

    # load last available deep
    def loadDeep(self):
        if self.args.dig and os.path.exists(self.work_dir + self.deep_file):
            self.deep = long(open(self.work_dir + self.deep_file).read())

    def saveEntry(self, batch):
        pass
        # with self.conn as cur:
        #    cur.executemany("INSERT INTO messages VALUES(?,?,?,?,?)",batch)
        # conn.commit()

    # save last available deep
    def saveDeep(self):
        with open(self.work_dir + self.deep_file, "wb") as f:
            f.write(str(self.deep))

    # save last available deep
    def outdated(self):
        return True if self.args.update and self.old_checkpoint != self.new_checkpoint else False

    ##
    # Argument parser
    #
    def parseArgs(self):
        parser = argparse.ArgumentParser(description="Parse image files.")
        parser.add_argument("-u", "--update", action="store_true", help="update by the new messages")
        parser.add_argument("-d", "--dig", action="store_true", help="continue form stop point")
        self.args = parser.parse_args()
        # if neither flags set
        # or set both of them
        # Exit
        if (not self.args.update and not self.args.dig) or (self.args.update and self.args.dig):
            raise Exception("Please, set one from update or dig.")

    def checkPhone(self, batch):
        new_batch = []
        for entry in batch:
            # Omit digits in unicode format
            str = unicode(entry[2]).replace(u'\u0417', "3")

            # Leave only numbers in string
            str = re.sub("[^0-9]", " ", str)

            i = 0
            phone = ""
            phones = []
            for c in str:
                if c.isdigit():
                    if i < self.max_step_size:
                        i = 0
                        phone = phone + c
                    elif len(phone):
                        phones.append(phone)
                        phone = c
                        i = 0
                elif len(phone):
                    i = i + 1

            if len(phone):
                phones.append(phone)

            lst = list(entry)
            a = [phone for phone in phones if len(phone) > 8]
            lst[3] = a[0] if len(a) else ""
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
    for i, x in enumerate(batch):
        new_batch.append((batch[i][0], batch[i][1], batch[i][2], labels[i][0]["label"]))
    return new_batch


def main():
    # Parse arguments
    # args.update
    # args.dig
    grab = Grab()
    try:
        grab.load()
        grab.run()
    except Exception as e:
        print(e)
    finally:
        if grab.args.dig: grab.saveDeep()


if __name__ == "__main__":
    main()
